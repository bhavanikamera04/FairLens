import pandas as pd
import numpy as np
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from collections import Counter


def _extract_shap_vals(shap_vals_raw: np.ndarray) -> np.ndarray:
    """Handles both modern (3D ndarray) and legacy (list) SHAP output formats."""
    if isinstance(shap_vals_raw, np.ndarray) and shap_vals_raw.ndim == 3:
        return shap_vals_raw[:, :, 1]   # Modern SHAP >=0.41: (samples, features, classes)
    elif isinstance(shap_vals_raw, list):
        return shap_vals_raw[1] if len(shap_vals_raw) > 1 else shap_vals_raw[0]
    return shap_vals_raw


def _shap_consistency_check(X: pd.DataFrame, y: pd.Series, n_runs: int = 20) -> dict:
    """
    Runs SHAP on n_runs bootstrap samples to check if the top feature is stable.
    
    HONEST INTERPRETATION:
    - Consistent top feature = reliable ASSOCIATION signal (not causation)
    - Inconsistent top feature = even the association is unreliable
    """
    top_features = []

    for _ in range(n_runs):
        idx = np.random.choice(len(X), size=len(X), replace=True)
        X_boot = X.iloc[idx].reset_index(drop=True)
        y_boot = y.iloc[idx].reset_index(drop=True)

        try:
            m = RandomForestClassifier(n_estimators=30, random_state=None)
            m.fit(X_boot, y_boot)
            exp = shap.TreeExplainer(m)
            sv = _extract_shap_vals(exp.shap_values(X))
            mean_abs = np.abs(sv).mean(axis=0)
            top_features.append(X.columns[np.argmax(mean_abs)])
        except Exception:
            continue

    if not top_features:
        return {"shap_confidence": "UNKNOWN", "shap_label": "⚠️ Could not assess SHAP stability"}

    counts = Counter(top_features)
    top_feature, top_count = counts.most_common(1)[0]
    consistency_pct = top_count / len(top_features)

    if consistency_pct >= 0.75:
        shap_confidence = "HIGH"
        shap_label = f"High model influence ({int(consistency_pct*100)}% of runs)"
    elif consistency_pct >= 0.5:
        shap_confidence = "MEDIUM"
        shap_label = f"Moderate model influence ({int(consistency_pct*100)}% of runs)"
    else:
        shap_confidence = "LOW"
        shap_label = f"Low model influence ({int(consistency_pct*100)}% of runs)"

    return {
        "shap_confidence":    shap_confidence,
        "shap_label":         shap_label,
        "top_feature":        top_feature,
        "consistency_pct":    float(consistency_pct),
        "feature_vote_counts": dict(counts),
        # CRITICAL DISCLAIMER — system must be intellectually honest
        "note": "This reflects model behavior, not causal effect.",
        "interpretation_note": (
            "SHAP identifies features ASSOCIATED with prediction differences between groups. "
            "This is NOT proof of causation. Use the What-If Simulation to test causal impact: "
            "if DI improves after dropping this feature, that is intervention-based evidence."
        )
    }


def run_root_cause_analysis(df: pd.DataFrame, protected_col: str, target_col: str, priv_val: str):
    """
    Uses SHAP to determine which features are most ASSOCIATED with outcome disparity.
    Also runs a consistency check to assess whether the signal is reliable.

    IMPORTANT: This system reports associations, not causes.
    Use the simulation endpoint to test causal hypotheses via intervention.
    """
    df_clean = df.copy().dropna()
    df_clean = df_clean.reset_index(drop=True)
    priv_mask = df_clean[protected_col].astype(str) == str(priv_val)

    encoders = {}
    for col in df_clean.columns:
        if not pd.api.types.is_numeric_dtype(df_clean[col]):
            encoders[col] = LabelEncoder()
            df_clean[col] = encoders[col].fit_transform(df_clean[col].astype(str))

    X = df_clean.drop(columns=[target_col])
    y = df_clean[target_col]

    # Main model + SHAP
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)

    explainer = shap.TreeExplainer(model)
    shap_vals = _extract_shap_vals(explainer.shap_values(X))

    shap_df = pd.DataFrame(shap_vals, columns=X.columns)
    priv_mean_shap   = shap_df[priv_mask].mean()
    unpriv_mean_shap = shap_df[~priv_mask].mean()
    shap_diff = (priv_mean_shap - unpriv_mean_shap).abs().sort_values(ascending=False)

    # SHAP consistency check across bootstrap runs
    consistency = _shap_consistency_check(X, y, n_runs=20)

    return {
        "feature_shap_diff":  {k: float(v) for k, v in shap_diff.to_dict().items()},
        "shap_stability":     consistency
    }
