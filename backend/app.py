from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd
import tempfile
import os
import json
import uuid
import numpy as np

def clean_json(obj):
    """
    Recursively replace NaN, inf, -inf with None
    so JSON can serialize properly
    """
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json(v) for v in obj]
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    return obj

from data_pipeline.ingestion import ingest_data, validate_schema
from core_engine.disparate_impact import calculate_disparate_impact
from core_engine.conditional_fairness import calculate_conditional_fairness
from core_engine.proxy_bias import detect_proxies
from explainability.root_cause import run_root_cause_analysis
from simulation.simulator import simulate_feature_drop
from core_engine.stability import bootstrap_di_stability

def compute_confidence(df):
    n = len(df)
    if n < 30:
        return "CRITICAL_LOW", "Dataset too small for any reliable inference. Analysis gated.", False
    elif n < 100:
        return "LOW", "Small sample size. High risk of coincidental patterns.", True
    elif n < 500:
        return "MEDIUM", "Adequate sample size. Results are indicative but require validation.", True
    return "HIGH", "Robust sample size for high-confidence statistical auditing.", True

app = FastAPI(title="FairLens 2.0 API", description="Production-Grade Fairness Audit & Decision Intelligence System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for hackathon purposes. Use Redis/S3 for production.
DATA_STORE = {}

@app.get("/")
def read_root():
    return {"status": "FairLens API is running"}

@app.post("/api/v1/audit/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Save to temp file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
        
    try:
        df = ingest_data(temp_path)
        # We would validate schema here, but we need rules. Skipping for generic upload.
        
        # Use UUID to prevent same-filename overwrite
        dataset_id = f"{uuid.uuid4().hex}_{file.filename}"
        DATA_STORE[dataset_id] = df
        
        return {
            "dataset_id": dataset_id,
            "columns": list(df.columns),
            "rows": len(df),
            "preview": df.head(5).to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/api/v1/audit/run")
async def run_audit(
    dataset_id: str = Form(...),
    protected_col: str = Form(...),
    target_col: str = Form(...),
    priv_val: str = Form(...),
    fav_outcome: str = Form(...),
    qualification_cols: str = Form("[]") # JSON string of list
):
    if dataset_id not in DATA_STORE:
        raise HTTPException(status_code=404, detail="Dataset not found. Please upload again.")
        
    df = DATA_STORE[dataset_id]
    
    try:
        qual_cols = json.loads(qualification_cols)

        # Validate columns exist before running any analysis
        for col_name, col_val in [(protected_col, priv_val), (target_col, fav_outcome)]:
            if col_name not in df.columns:
                raise HTTPException(status_code=400, detail=f"Column '{col_name}' not found in dataset. Available columns: {list(df.columns)}")
        
        di_results = calculate_disparate_impact(df, protected_col, target_col, priv_val, fav_outcome)
        
        proxy_results = detect_proxies(df, protected_col, target_col)
        
        cf_results = {}
        if qual_cols:
            cf_results = calculate_conditional_fairness(df, protected_col, target_col, qual_cols, priv_val, fav_outcome)
            
        rca_results = run_root_cause_analysis(df, protected_col, target_col, priv_val)
        # rca_results now returns {"feature_shap_diff": {...}, "shap_stability": {...}}
        feature_diffs = rca_results.get("feature_shap_diff", {})
        shap_stability = rca_results.get("shap_stability", {})

        # Confidence Score & Decision Gating
        confidence, confidence_reason, decision_allowed = compute_confidence(df)

        # Bootstrap stability for DI
        di_stability = bootstrap_di_stability(df, protected_col, target_col, priv_val, fav_outcome, n_runs=30)

        # If decision is gated, we return early with minimal data to prevent misleading insights
        if not decision_allowed:
            return clean_json({
                "dataset_info": {
                    "rows": len(df),
                    "confidence": confidence,
                    "confidence_reason": confidence_reason,
                    "decision_allowed": False
                },
                "disparate_impact": di_results, # Show raw DI but with heavy warning
                "recommendations": ["DATASET TOO SMALL: No reliable recommendations can be generated. Please upload at least 30 rows of data."]
            })

        # Enhanced Proxy Risk Logic: Connect proxy detection with SHAP
        proxy_risks = []
        for feature, mi in proxy_results.items():
            shap_val = feature_diffs.get(feature, 0)
            if mi > 0.3 and shap_val > 0.02: 
                proxy_risks.append({
                    "feature": feature,
                    "risk": "HIGH",
                    "impact": f"HYPOTHESIS: Dropping '{feature}' may improve fairness. Test this in Simulation."
                })

        # Recommendations Logic — hypothesis-driven
        recommendations = []

        # DI recommendation
        di_val = di_results.get("disparate_impact", 1.0)
        if di_val < 0.8:
            recommendations.append(
                f"HYPOTHESIS: Disparate Impact ({di_val:.2f}) indicates potential systemic bias. "
                "ACTION: Run simulations on top model drivers to identify intervention points."
            )

        # Proxy recommendation
        if proxy_risks:
            high_risk = [r for r in proxy_risks if r['risk'] == "HIGH"]
            if high_risk:
                recommendations.append(
                    f"OBSERVATION: '{high_risk[0]['feature']}' is a high-risk proxy. "
                    f"TEST: Does removing '{high_risk[0]['feature']}' improve the DI ratio? (Use Simulation Panel)."
                )

        # SHAP RCA recommendation
        if feature_diffs:
            top_cause = list(feature_diffs.keys())[0]
            recommendations.append(
                f"MODEL RELIANCE: The model relies heavily on '{top_cause}' for predictions. "
                "DISCLAIMER: This is an associative signal. It does NOT prove real-world causation. "
                "VERIFICATION: Use the 'What-If' simulator to test if this feature is a necessary driver of disparity."
            )

        results = {
            "dataset_info": {
                "rows": len(df),
                "confidence": confidence,
                "confidence_reason": confidence_reason,
                "decision_allowed": True
            },
            "disparate_impact": di_results,
            "di_stability": di_stability,
            "proxy_bias": proxy_results,
            "proxy_risks": proxy_risks,
            "conditional_fairness": cf_results,
            "root_cause_analysis": {
                "feature_shap_diff": feature_diffs,
                "shap_stability": shap_stability
            },
            "recommendations": recommendations
        }
        
        return clean_json(results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running audit: {str(e)}")

@app.post("/api/v1/audit/simulate")
async def simulate_scenario(
    dataset_id: str = Form(...),
    protected_col: str = Form(...),
    target_col: str = Form(...),
    priv_val: str = Form(...),
    fav_outcome: str = Form(...),
    feature_to_drop: str = Form(...)
):
    if dataset_id not in DATA_STORE:
        raise HTTPException(status_code=404, detail="Dataset not found. Please upload again.")
        
    df = DATA_STORE[dataset_id]
    
    try:
        # Validate columns before simulation
        for col_name in [protected_col, target_col]:
            if col_name not in df.columns:
                raise HTTPException(status_code=400, detail=f"Column '{col_name}' not found. Available: {list(df.columns)}")
        if feature_to_drop not in df.columns:
            raise HTTPException(status_code=400, detail=f"Feature '{feature_to_drop}' not found. Available: {list(df.columns)}")

        simulated_df = simulate_feature_drop(df, feature_to_drop)
        DATA_STORE[f"{dataset_id}_simulated"] = simulated_df
        
        # Recalculate DI
        di_results = calculate_disparate_impact(simulated_df, protected_col, target_col, priv_val, fav_outcome)
        
        return clean_json({
            "message": f"Simulation running without '{feature_to_drop}'",
            "new_dataset_id": f"{dataset_id}_simulated",
            "new_disparate_impact": di_results
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
