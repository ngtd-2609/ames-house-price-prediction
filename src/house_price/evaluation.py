"""Metric va uncertainty evaluation dung chung."""
from __future__ import annotations

import math
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error, r2_score

from .config import RANDOM_STATE


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    prediction = np.maximum(np.asarray(y_pred, dtype=float), 0)
    return {
        "RMSE": float(math.sqrt(mean_squared_error(y_true, prediction))),
        "MAE": float(mean_absolute_error(y_true, prediction)),
        "R2": float(r2_score(y_true, prediction)),
        "RMSLE": float(math.sqrt(mean_squared_log_error(y_true, prediction))),
    }


def bootstrap_metric_ci(y_true, y_pred, n_bootstrap: int = 1000, random_state: int = RANDOM_STATE) -> dict:
    """Bootstrap percentile 95% CI cho RMSE/MAE; deterministic theo seed."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.maximum(np.asarray(y_pred, dtype=float), 0)
    rng = np.random.default_rng(random_state)
    rmse_values, mae_values = [], []
    n = len(y_true)
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        rmse_values.append(math.sqrt(mean_squared_error(y_true[idx], y_pred[idx])))
        mae_values.append(mean_absolute_error(y_true[idx], y_pred[idx]))
    def ci(values):
        lo, hi = np.percentile(values, [2.5, 97.5])
        return {"lower": float(lo), "upper": float(hi)}
    return {"RMSE_95CI": ci(rmse_values), "MAE_95CI": ci(mae_values), "n_bootstrap": n_bootstrap}
