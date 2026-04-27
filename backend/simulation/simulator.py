import pandas as pd
from typing import Dict, Any

def simulate_feature_drop(df: pd.DataFrame, feature_to_drop: str) -> pd.DataFrame:
    """
    Simulates dropping a feature from the dataset.
    """
    if feature_to_drop in df.columns:
        return df.drop(columns=[feature_to_drop])
    return df

def simulate_reweighting(df: pd.DataFrame, protected_col: str, target_col: str, priv_val: str, fav_outcome: str) -> Dict[str, float]:
    """
    Calculates sample weights to reweigh the dataset for disparate impact mitigation.
    Returns the weights mapped to each group-outcome combination.
    """
    # Compute counts
    n = len(df)
    n_p = len(df[df[protected_col] == priv_val])
    n_u = len(df[df[protected_col] != priv_val])
    n_f = len(df[df[target_col] == fav_outcome])
    n_uf = len(df[df[target_col] != fav_outcome])

    # Avoid div by zero
    if n_p == 0 or n_u == 0 or n_f == 0 or n_uf == 0:
        return {}

    # Expected probabilities if protected_col and target_col were independent
    w_p_f = (n_p * n_f / n) / len(df[(df[protected_col] == priv_val) & (df[target_col] == fav_outcome)]) if len(df[(df[protected_col] == priv_val) & (df[target_col] == fav_outcome)]) > 0 else 1.0
    w_p_uf = (n_p * n_uf / n) / len(df[(df[protected_col] == priv_val) & (df[target_col] != fav_outcome)]) if len(df[(df[protected_col] == priv_val) & (df[target_col] != fav_outcome)]) > 0 else 1.0
    w_u_f = (n_u * n_f / n) / len(df[(df[protected_col] != priv_val) & (df[target_col] == fav_outcome)]) if len(df[(df[protected_col] != priv_val) & (df[target_col] == fav_outcome)]) > 0 else 1.0
    w_u_uf = (n_u * n_uf / n) / len(df[(df[protected_col] != priv_val) & (df[target_col] != fav_outcome)]) if len(df[(df[protected_col] != priv_val) & (df[target_col] != fav_outcome)]) > 0 else 1.0

    return {
        f"priv_{fav_outcome}": w_p_f,
        f"priv_not_{fav_outcome}": w_p_uf,
        f"unpriv_{fav_outcome}": w_u_f,
        f"unpriv_not_{fav_outcome}": w_u_uf
    }
