"""Executable model-selection policy used before the test split is opened."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json

import pandas as pd


_REQUIRED_COLUMNS = {"Model", "RMSE", "CV_RMSE_mean", "Best_params"}


@dataclass(frozen=True)
class ModelSelectionPolicy:
    """Only criteria that are actually executed by :func:`select_final_model`."""

    primary_metric: str = "validation_RMSE"
    validation_tolerance: float = 0.02
    ridge_tie_break_requires_cv_not_worse: bool = True
    uses_test: bool = False
    candidate_filter: str = "Predefined tuned candidates: ElasticNet and Ridge; test is unavailable during selection."
    tie_breaker_order: tuple[str, ...] = ("validation_RMSE", "CV_RMSE_mean")

    def as_output_dict(self, locked_model: str, locked_params: dict) -> dict:
        payload = asdict(self)
        payload.update({
            "ridge_tie_break_rule": (
                "Select Ridge only when its validation RMSE is within validation_tolerance "
                "of the best tuned validation RMSE and its CV RMSE mean is no worse."
            ),
            "locked_model": locked_model,
            "locked_params": locked_params,
            "selection_locked_at_utc": datetime.now(timezone.utc).isoformat(),
        })
        payload["tie_breaker_order"] = list(payload["tie_breaker_order"])
        return payload


def _validate_tuning_table(tuning_table: pd.DataFrame) -> None:
    if not isinstance(tuning_table, pd.DataFrame):
        raise TypeError("tuning_table must be a pandas.DataFrame")
    if tuning_table.empty:
        raise ValueError("tuning_table must not be empty")
    missing = sorted(_REQUIRED_COLUMNS - set(tuning_table.columns))
    if missing:
        raise ValueError(f"tuning_table missing required columns: {', '.join(missing)}")
    if tuning_table[["RMSE", "CV_RMSE_mean"]].isna().any().any():
        raise ValueError("RMSE and CV_RMSE_mean must be finite values")


def select_final_model(
    tuning_table: pd.DataFrame,
    policy: ModelSelectionPolicy | None = None,
) -> tuple[str, pd.Series, dict]:
    """Select the locked model using validation RMSE and the documented Ridge tie-break.

    Test metrics are intentionally absent from the function signature and policy.
    """
    _validate_tuning_table(tuning_table)
    policy = policy or ModelSelectionPolicy()
    if policy.validation_tolerance < 0:
        raise ValueError("validation_tolerance must be non-negative")

    table = tuning_table.sort_values(["RMSE", "CV_RMSE_mean", "Model"], kind="mergesort").reset_index(drop=True)
    best = table.iloc[0]
    selected_name = str(best["Model"]).replace(" (Tuned)", "")
    selected_row = best

    ridge_rows = table[table["Model"] == "Ridge (Tuned)"]
    if not ridge_rows.empty:
        ridge = ridge_rows.iloc[0]
        rmse_ok = float(ridge["RMSE"]) <= float(best["RMSE"]) * (1 + policy.validation_tolerance)
        cv_ok = (
            not policy.ridge_tie_break_requires_cv_not_worse
            or float(ridge["CV_RMSE_mean"]) <= float(best["CV_RMSE_mean"])
        )
        if rmse_ok and cv_ok:
            selected_name = "Ridge"
            selected_row = ridge

    try:
        params = json.loads(str(selected_row["Best_params"]))
    except json.JSONDecodeError as exc:
        raise ValueError("Best_params must contain valid JSON") from exc
    if not isinstance(params, dict):
        raise ValueError("Best_params JSON must decode to an object")

    policy_output = policy.as_output_dict(selected_name, params)
    return selected_name, selected_row, policy_output
