import pandas as pd
import numpy as np
from core_engine.disparate_impact import calculate_disparate_impact


def bootstrap_di_stability(
    df: pd.DataFrame,
    protected_col: str,
    target_col: str,
    priv_val: str,
    fav_outcome: str,
    n_runs: int = 30
) -> dict:
    """
    Bootstrap resampling to test whether the Disparate Impact metric is stable.

    Rationale:
    - A DI of 0.66 from 8 rows could be 0.4 or 0.9 on a slightly different sample.
    - High std_DI => your conclusion is data-sensitive and unreliable.
    - Low std_DI  => the signal is real and robust.

    This does NOT prove causation — it only tells you whether the measured
    association is consistent across data variations.
    """
    di_values = []

    for _ in range(n_runs):
        sample = df.sample(frac=1, replace=True).reset_index(drop=True)
        result = calculate_disparate_impact(
            sample, protected_col, target_col, priv_val, fav_outcome
        )
        # Only collect valid, non-degenerate results
        if "error" not in result and result.get("disparate_impact", 0) > 0:
            di_values.append(result["disparate_impact"])

    if len(di_values) < 5:
        return {
            "error": "Too few valid bootstrap samples — dataset may be too small or degenerate.",
            "confidence": "UNKNOWN",
            "signal": "Cannot assess stability with this data."
        }

    mean_di = float(np.mean(di_values))
    std_di  = float(np.std(di_values))
    min_di  = float(np.min(di_values))
    max_di  = float(np.max(di_values))

    # Confidence thresholds based on coefficient of variation relative to the 0.8 boundary
    if std_di < 0.05:
        confidence = "STABLE"
        label = "✅ Stable Audit"
        explanation = (
            f"DI is stable across {n_runs} bootstrap samples (std={std_di:.3f}). "
            "This association is robust to data variation."
        )
    elif std_di < 0.15:
        confidence = "MODERATE"
        label = "⚠️ Moderate Variance"
        explanation = (
            f"DI varies moderately (std={std_di:.3f}). "
            "Conclusions may change with more data. Interpret with caution."
        )
    else:
        confidence = "UNSTABLE"
        label = "❌ High Instability"
        explanation = (
            f"DI is highly unstable (std={std_di:.3f}). "
            "Results are sensitive to data changes — collect more data before drawing conclusions."
        )

    return {
        "mean_DI":    mean_di,
        "std_DI":     std_di,
        "min_DI":     min_di,
        "max_DI":     max_di,
        "n_runs":     len(di_values),
        "confidence": confidence,
        "label":      label,
        "explanation": explanation
    }
