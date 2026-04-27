import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np

def calculate_conditional_fairness(df: pd.DataFrame, protected_col: str, target_col: str, qualification_cols: list, priv_val: str, fav_outcome: str):
    """
    Evaluates conditional fairness using Logistic Regression with StandardScaler.
    Checks if the protected attribute is statistically significant after controlling for qualifications.
    Scaling ensures coefficients are comparable and the threshold is meaningful.
    """
    df_clean = df.copy().dropna(subset=qualification_cols + [protected_col, target_col])
    
    # Encode categorical features
    encoders = {}
    for col in qualification_cols + [protected_col, target_col]:
        if not pd.api.types.is_numeric_dtype(df_clean[col]):
            encoders[col] = LabelEncoder()
            df_clean[col] = encoders[col].fit_transform(df_clean[col].astype(str))
            
    X = df_clean[qualification_cols + [protected_col]]
    y = df_clean[target_col]
    
    # Scale features so coefficients are on the same scale (mean=0, std=1)
    # Without this, raw coef magnitude is meaningless across differently-scaled features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X_scaled, y)
    
    protected_idx = list(X.columns).index(protected_col)
    protected_coef = model.coef_[0][protected_idx]
    
    return {
        "protected_attribute_coefficient": float(protected_coef),
        "status": "Protected attribute still influences outcome after controlling selected features" if abs(protected_coef) > 0.5 else "No strong residual influence detected",
        "conditional_fairness_violated": bool(abs(protected_coef) > 0.5),
        "warning": "Result depends on selected features. Missing variables may affect validity."
    }
