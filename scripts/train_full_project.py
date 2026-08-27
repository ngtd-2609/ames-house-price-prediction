"""Canonical training orchestrator for the house-price project.

This file intentionally contains orchestration only. Reusable scientific logic
lives in src/house_price so notebooks, scripts and docs share one source of
truth.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np

from house_price.artifacts import save_input_schema
from house_price.config import ID_COLUMN, TARGET
from house_price.data import load_house_data, split_xy
from house_price.diagnostics import evaluate_locked_model
from house_price.eda import create_training_eda
from house_price.modeling import model_definitions
from house_price.reporting import (
    build_summary_payload,
    compute_cv_stability,
    save_canonical_artifact,
    save_data_hashes,
    save_deployment_architecture_figure,
    save_feature_engineering_table,
    write_json,
)
from house_price.selection import ModelSelectionPolicy, select_final_model
from house_price.tuning import evaluate_candidates, tune_candidates
from house_price.validation import validate_splits

OUTPUT = ROOT / "outputs"
FIGURES = OUTPUT / "figures"
TABLES = OUTPUT / "tables"
OUT_MODELS = OUTPUT / "models"
DEPLOY_MODELS = ROOT / "models"
for directory in (FIGURES, TABLES, OUT_MODELS, DEPLOY_MODELS):
    directory.mkdir(parents=True, exist_ok=True)


def load_and_validate_project_data() -> tuple:
    """Load three fixed splits and write deterministic data-integrity artifacts."""
    train = load_house_data("house_train_80.csv")
    validation = load_house_data("house_validation_10.csv")
    test = load_house_data("house_test_10.csv")
    integrity = validate_splits(train, validation, test)
    hashes = save_data_hashes(ROOT, TABLES, ["house_train_80.csv", "house_validation_10.csv", "house_test_10.csv"])
    write_json(
        OUTPUT / "data_integrity.json",
        {**integrity, "hashes": hashes, "split_origin_note": "Ba split duoc cung cap san; repository khong co ma goc tao split, do do khong tu y tai chia lai."},
    )
    return train, validation, test, hashes


def main() -> None:
    run_started = time.perf_counter()
    train, validation, test, hashes = load_and_validate_project_data()

    target_stats, corr_table, missing = create_training_eda(train, validation, TABLES, FIGURES)
    X_train, y_train = split_xy(train)
    X_val, y_val = split_xy(validation)
    definitions = model_definitions()

    # TEST LOCK: no X_test/y_test or target diagnostics are accessed before model selection.
    results, _ = evaluate_candidates(X_train, y_train, X_val, y_val, definitions, TABLES, FIGURES)
    tuning, tuned = tune_candidates(definitions, X_train, y_train, X_val, y_val, TABLES)
    selected_name, selected_row, selection_policy = select_final_model(tuning, ModelSelectionPolicy())
    selected_estimator = tuned[selected_name]
    selected_validation = {m: float(selected_row[m]) for m in ["RMSE", "MAE", "R2", "RMSLE"]}
    selected_params = json.loads(str(selected_row["Best_params"]))
    write_json(OUTPUT / "model_selection_policy.json", selection_policy)

    # TEST UNLOCK: final holdout is opened only after selected_name/params/policy are persisted.
    X_test, y_test = split_xy(test)
    ids_test = test[ID_COLUMN].copy()

    print("FINAL_EVALUATION_START", flush=True)
    final_estimator, test_metrics, ci, predictions, quartile, top_errors, importance, final_fit_s, final_predict_s = evaluate_locked_model(
        selected_estimator,
        selected_name,
        X_train,
        y_train,
        X_val,
        y_val,
        X_test,
        y_test,
        ids_test,
        test,
        TABLES,
        FIGURES,
    )
    print("FINAL_EVALUATION_DONE", flush=True)

    stability = compute_cv_stability(X_train, y_train, definitions[selected_name], selected_params, TABLES)
    deploy_model, reload_pred = save_canonical_artifact(final_estimator, DEPLOY_MODELS, OUT_MODELS, X_test, predictions.PredictedSalePrice)
    schema = save_input_schema(train, DEPLOY_MODELS)
    save_feature_engineering_table(TABLES)
    save_deployment_architecture_figure(FIGURES, selected_name)

    duration = time.perf_counter() - run_started
    summary = build_summary_payload(
        ROOT,
        train,
        validation,
        test,
        X_train,
        selected_name,
        selected_params,
        selection_policy,
        selected_validation,
        stability,
        test_metrics,
        ci,
        target_stats,
        corr_table,
        missing,
        results,
        tuning,
        importance,
        top_errors,
        quartile,
        hashes,
        deploy_model,
        schema,
        reload_pred,
        duration,
        final_fit_s,
        final_predict_s,
    )
    write_json(OUTPUT / "summary.json", summary)
    write_json(DEPLOY_MODELS / "training_summary.json", summary)
    print("ANALYSIS_COMPLETED")
    print(json.dumps({"selected_model": selected_name, "validation": selected_validation, "test": test_metrics, "runtime_seconds": duration}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
