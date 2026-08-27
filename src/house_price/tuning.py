"""Benchmarking and hyperparameter tuning logic."""
from __future__ import annotations

import json
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import KFold, RandomizedSearchCV

from .config import RANDOM_STATE
from .evaluation import regression_metrics
from .modeling import build_end_to_end_estimator, tuning_space
from .plotting import save_figure


def evaluate_candidates(X_train, y_train, X_val, y_val, definitions: dict[str, object], tables_dir, figures_dir) -> tuple[pd.DataFrame, dict[str, object]]:
    """Benchmark candidate models on validation without using test data."""
    baseline = DummyRegressor(strategy="median").fit(np.zeros((len(y_train), 1)), y_train)
    baseline_row = {
        "Model": "DummyRegressor (median)",
        "Train_RMSE": regression_metrics(y_train, baseline.predict(np.zeros((len(y_train), 1))))["RMSE"],
        **regression_metrics(y_val, baseline.predict(np.zeros((len(y_val), 1)))),
        "Fit_seconds": 0.0,
        "Predict_seconds": 0.0,
    }
    rows = [baseline_row]
    fitted: dict[str, object] = {}
    for name, definition in definitions.items():
        estimator = build_end_to_end_estimator(X_train, definition)
        start = time.perf_counter()
        estimator.fit(X_train, y_train)
        fit_s = time.perf_counter() - start
        start = time.perf_counter()
        train_pred = estimator.predict(X_train)
        val_pred = estimator.predict(X_val)
        pred_s = time.perf_counter() - start
        rows.append({"Model": name, "Train_RMSE": regression_metrics(y_train, train_pred)["RMSE"], **regression_metrics(y_val, val_pred), "Fit_seconds": fit_s, "Predict_seconds": pred_s})
        fitted[name] = estimator
    results = pd.DataFrame(rows)
    results["RMSE_gap"] = results["RMSE"] - results["Train_RMSE"]
    results["Relative_to_dummy_RMSE_improvement_pct"] = (baseline_row["RMSE"] - results["RMSE"]) / baseline_row["RMSE"] * 100
    results = results.sort_values("RMSE").reset_index(drop=True)
    results.to_csv(tables_dir / "validation_model_comparison.csv", index=False, encoding="utf-8-sig")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.barplot(data=results.head(10), y="Model", x="RMSE", ax=axes[0], color="#5B9BD5")
    axes[0].set_title("Validation RMSE - thấp hơn tốt hơn")
    axes[0].set_xlabel("RMSE (USD)"); axes[0].set_ylabel("")
    sns.barplot(data=results.head(10), y="Model", x="R2", ax=axes[1], color="#70AD47")
    axes[1].set_title("Validation R² - cao hơn tốt hơn")
    axes[1].set_xlabel("R²"); axes[1].set_ylabel("")
    save_figure(figures_dir, "07_validation_model_comparison.png")
    return results, fitted


def tune_candidates(definitions: dict[str, object], X_train, y_train, X_val, y_val, tables_dir) -> tuple[pd.DataFrame, dict[str, object]]:
    """Tune selected stable candidates under a predefined CV protocol."""
    ranked = [name for name in ["ElasticNet", "Ridge"] if name in definitions]
    if not ranked:
        raise ValueError("No supported tuning candidates found; expected ElasticNet and/or Ridge")
    cv = KFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
    tuned: dict[str, object] = {}
    rows: list[dict] = []
    for name in ranked:
        print(f"TUNING_START {name}", flush=True)
        estimator = build_end_to_end_estimator(X_train, definitions[name])
        space = tuning_space(name)
        combinations = int(np.prod([len(v) for v in space.values()]))
        max_iter = {"ElasticNet": 3, "Ridge": 3}.get(name, 3)
        search = RandomizedSearchCV(
            estimator,
            space,
            n_iter=min(max_iter, combinations),
            scoring="neg_root_mean_squared_error",
            cv=cv,
            random_state=RANDOM_STATE,
            n_jobs=1,
            refit=True,
            return_train_score=True,
        )
        start = time.perf_counter()
        search.fit(X_train, y_train)
        elapsed = time.perf_counter() - start
        val_pred = search.best_estimator_.predict(X_val)
        metrics = regression_metrics(y_val, val_pred)
        best_idx = search.best_index_
        rows.append({
            "Model": f"{name} (Tuned)",
            **metrics,
            "CV_RMSE_mean": float(-search.cv_results_["mean_test_score"][best_idx]),
            "CV_RMSE_std": float(search.cv_results_["std_test_score"][best_idx]),
            "CV_train_RMSE_mean": float(-search.cv_results_["mean_train_score"][best_idx]),
            "Search_seconds": elapsed,
            "Candidates_evaluated": int(len(search.cv_results_["params"])),
            "Best_params": json.dumps(search.best_params_, ensure_ascii=False, default=str),
        })
        tuned[name] = search.best_estimator_
        print(f"TUNING_DONE {name} {elapsed:.2f}s RMSE={metrics['RMSE']:.2f}", flush=True)
    table = pd.DataFrame(rows).sort_values(["RMSE", "CV_RMSE_mean"]).reset_index(drop=True)
    table.to_csv(tables_dir / "tuning_results.csv", index=False, encoding="utf-8-sig")
    return table, tuned
