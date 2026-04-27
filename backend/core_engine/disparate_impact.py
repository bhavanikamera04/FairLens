import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

def calculate_disparate_impact(df: pd.DataFrame, protected_col: str, target_col: str, priv_val: str, fav_outcome: str):
    """
    Calculates Disparate Impact with Confidence Intervals and Statistical Significance.
    """
    # Avoid mutating original dataframe by creating series
    prot_series = df[protected_col].astype(str)
    targ_series = df[target_col].astype(str)
    priv_val = str(priv_val)
    fav_outcome = str(fav_outcome)
                      
    priv_mask = prot_series == priv_val
    unpriv_mask = prot_series != priv_val

    if priv_mask.sum() == 0 or unpriv_mask.sum() == 0:
        return {"error": "Missing privileged or unprivileged group in data."}

    priv_targ = targ_series[priv_mask]
    unpriv_targ = targ_series[unpriv_mask]

    p_p = (priv_targ == fav_outcome).sum() / len(priv_targ)
    p_u = (unpriv_targ == fav_outcome).sum() / len(unpriv_targ)

    if p_p == 0:
        di = None  # Undefined/Infinity case
    elif p_u == 0:
        di = 0.0
    else:
        di = p_u / p_p

    # Chi-square test
    contingency = pd.crosstab(priv_mask, targ_series == fav_outcome)
    try:
        chi2, p_val, dof, expected = chi2_contingency(contingency)
    except ValueError:
        p_val = None

    # Confidence Interval (Delta method)
    n_p, n_u = len(priv_targ), len(unpriv_targ)
    # Avoid div by zero in SE calculation
    try:
        if di > 0 and p_p > 0 and p_u > 0:
            se = np.sqrt(((1 - p_u) / (n_u * p_u)) + ((1 - p_p) / (n_p * p_p)))
            ci_lower = np.exp(np.log(di) - 1.96 * se)
            ci_upper = np.exp(np.log(di) + 1.96 * se)
        else:
            ci_lower, ci_upper = None, None
    except Exception:
        ci_lower, ci_upper = None, None

    # Statistical significance reliability note
    p_value_note = None
    if len(df) < 50:
        p_value_note = "Statistical significance unreliable due to small sample size"

    return {
        "disparate_impact": float(di),
        "p_value": float(p_val) if p_val is not None else None,
        "significant": bool(p_val < 0.05) if p_val is not None else False,
        "p_value_note": p_value_note,
        "ci_lower": float(ci_lower) if ci_lower is not None else None,
        "ci_upper": float(ci_upper) if ci_upper is not None else None,
        "priv_rate": float(p_p),
        "unpriv_rate": float(p_u)
    }
