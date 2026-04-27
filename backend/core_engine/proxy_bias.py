import pandas as pd
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import LabelEncoder

def detect_proxies(df: pd.DataFrame, protected_col: str, target_col: str):
    """
    Detects proxy variables for the protected column using Mutual Information.
    """
    df_clean = df.copy().dropna()
    
    encoders = {}
    for col in df_clean.columns:
        if not pd.api.types.is_numeric_dtype(df_clean[col]):
            encoders[col] = LabelEncoder()
            df_clean[col] = encoders[col].fit_transform(df_clean[col].astype(str))
            
    X = df_clean.drop(columns=[protected_col, target_col])  # fix: exclude target to prevent leakage
    y = df_clean[protected_col]
    
    mi_scores = mutual_info_classif(X, y, random_state=42)
    proxy_scores = dict(zip(X.columns, mi_scores))
    
    # Sort descending and cast to native float
    proxy_scores = {k: float(v) for k, v in sorted(proxy_scores.items(), key=lambda item: item[1], reverse=True)}
    
    return proxy_scores
