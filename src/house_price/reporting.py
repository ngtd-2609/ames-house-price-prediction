"""Canonical artifact/output reporting utilities."""
from __future__ import annotations

import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sklearn
from sklearn.model_selection import KFold, cross_validate

from .artifacts import save_input_schema
from .config import ENGINEERED_FEATURES, RANDOM_STATE
from .data import sha256_file
from .features import engineer_features
from .modeling import build_end_to_end_estimator
from .plotting import save_figure


def save_data_hashes(root: Path, tables_dir: Path, filenames: list[str]) -> list[dict]:
    hashes = []
    for name in filenames:
        path = root / "data" / name
        hashes.append({"file": f"data/{name}", "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    pd.DataFrame(hashes).to_csv(tables_dir / "data_hashes.csv", index=False)
    return hashes


def save_feature_engineering_table(tables_dir: Path) -> None:
    pd.DataFrame([
        ["HouseAge", "YrSold - YearBuilt", "Tuổi nhà tại thời điểm bán"], ["RemodAge", "YrSold - YearRemodAdd", "Tuổi từ lần cải tạo"],
        ["GarageAge", "YrSold - GarageYrBlt", "Tuổi gara"], ["TotalSF", "TotalBsmtSF + 1stFlrSF + 2ndFlrSF", "Tổng diện tích sàn"],
        ["TotalBathrooms", "Full + 0.5 Half + basement", "Tổng phòng tắm quy đổi"], ["TotalPorchSF", "Tổng 5 loại hiên/sàn", "Không gian hiên"],
        ["TotalOutdoorSF", "TotalPorchSF + PoolArea", "Không gian ngoài trời"], ["HasGarage/HasBsmt/HasFireplace/HasPool/Has2ndFloor/HasMasVnr", "Cờ 0/1", "Có/không tiện ích"],
        ["MoSold_sin/cos", "sin/cos(2π MoSold/12)", "Mã hóa chu kỳ tháng"],
    ], columns=["Feature", "Formula", "Meaning"]).to_csv(tables_dir / "feature_engineering.csv", index=False, encoding="utf-8-sig")


def save_deployment_architecture_figure(figures_dir: Path, selected_name: str) -> None:
    fig, ax = plt.subplots(figsize=(11, 3.2))
    ax.axis("off")
    labels = ["Raw Ames input\n79 features", "AmesFeatureEngineer\n+ 15 features", "Impute + scale\n+ one-hot", f"{selected_name}\nlog-target", "Predicted\nSalePrice (USD)"]
    xs = np.linspace(0.08, 0.92, len(labels))
    for x, label in zip(xs, labels):
        ax.text(x, 0.5, label, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="black"), transform=ax.transAxes)
    for a, b in zip(xs[:-1], xs[1:]):
        ax.annotate("", xy=(b - 0.08, 0.5), xytext=(a + 0.08, 0.5), xycoords=ax.transAxes, arrowprops=dict(arrowstyle="->"))
    ax.set_title("Artifact end-to-end: feature engineering nằm bên trong model đã lưu")
    save_figure(figures_dir, "13_deployment_architecture.png")


def compute_cv_stability(X_train, y_train, definition, selected_params: dict, tables_dir: Path) -> dict:
    print("CV_STABILITY_START", flush=True)
    cv = KFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
    stability_estimator = build_end_to_end_estimator(X_train, definition)
    stability_estimator.set_params(**selected_params)
    cv_scores = cross_validate(stability_estimator, X_train, y_train, cv=cv, scoring={"rmse": "neg_root_mean_squared_error", "mae": "neg_mean_absolute_error", "r2": "r2"}, return_train_score=True, n_jobs=1)
    stability = {
        "CV_RMSE_mean": float(-cv_scores["test_rmse"].mean()), "CV_RMSE_std": float(cv_scores["test_rmse"].std()),
        "CV_MAE_mean": float(-cv_scores["test_mae"].mean()), "CV_MAE_std": float(cv_scores["test_mae"].std()),
        "CV_R2_mean": float(cv_scores["test_r2"].mean()), "CV_R2_std": float(cv_scores["test_r2"].std()),
        "CV_train_RMSE_mean": float(-cv_scores["train_rmse"].mean()),
    }
    pd.DataFrame([stability]).to_csv(tables_dir / "selected_model_cv_stability.csv", index=False)
    print("CV_STABILITY_DONE", flush=True)
    return stability


def save_canonical_artifact(final_estimator, deploy_models_dir: Path, out_models_dir: Path, X_test: pd.DataFrame, expected_predictions: pd.Series) -> tuple[Path, list[float]]:
    deploy_models_dir.mkdir(parents=True, exist_ok=True)
    deploy_model = deploy_models_dir / "house_price_pipeline.joblib"
    joblib.dump(final_estimator, deploy_model)
    for duplicate in [out_models_dir / "best_house_price_model.joblib", deploy_models_dir / "basic_ridge_pipeline.joblib"]:
        if duplicate.exists():
            duplicate.unlink()
    reloaded = joblib.load(deploy_model)
    reload_pred = reloaded.predict(X_test.head(3))
    if not np.allclose(reload_pred, expected_predictions.head(3)):
        raise AssertionError("Reloaded artifact predictions differ from current predictions")
    return deploy_model, [float(v) for v in reload_pred]


def build_summary_payload(root: Path, train, validation, test, X_train, selected_name: str, selected_params: dict, selection_policy: dict, selected_validation: dict, stability: dict, test_metrics: dict, ci: dict, target_stats: dict, corr_table: pd.DataFrame, missing: pd.DataFrame, results: pd.DataFrame, tuning: pd.DataFrame, importance: pd.DataFrame, top_errors: pd.DataFrame, quartile: pd.DataFrame, hashes: list[dict], deploy_model: Path, schema: dict, reload_pred: list[float], duration: float, final_fit_s: float, final_predict_s: float) -> dict:
    engineered_sample = engineer_features(X_train.head(5))
    return {
        "canonical_result_source": "outputs/summary.json",
        "code_hashes": {"train_full_project.py": sha256_file(root / "scripts" / "train_full_project.py"), "src_house_price_artifacts.py": sha256_file(root / "src" / "house_price" / "artifacts.py")},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "pandas": pd.__version__, "numpy": np.__version__, "scikit_learn": sklearn.__version__, "random_state": RANDOM_STATE},
        "dataset": {"train_shape": list(train.shape), "validation_shape": list(validation.shape), "test_shape": list(test.shape), "total_rows": 1460, "input_features_raw": len(X_train.columns), "engineered_features_added": len(ENGINEERED_FEATURES), "engineered_feature_count": int(engineered_sample.shape[1]), "split_origin_reproducible": False},
        "data_hashes": hashes,
        "target_stats": target_stats,
        "top_correlations": corr_table.head(10).to_dict(orient="records"),
        "missing_top": missing.head(10).to_dict(orient="records"),
        "ranked_models": results.to_dict(orient="records"),
        "tuned_models": tuning.to_dict(orient="records"),
        "selected_model": selected_name,
        "selected_params": selected_params,
        "selection_policy": selection_policy,
        "selection_basis": "Model duoc khoa truoc khi mo test; selection policy executable nam trong outputs/model_selection_policy.json va src/house_price/selection.py.",
        "validation_metrics": selected_validation,
        "selected_model_cv_stability": stability,
        "test_metrics": test_metrics,
        "test_bootstrap_ci": ci,
        "top_features": importance.head(15).to_dict(orient="records"),
        "top_errors": top_errors.to_dict(orient="records"),
        "quartile_errors": quartile.to_dict(orient="records"),
        "artifact": {"path": "models/house_price_pipeline.joblib", "canonical_only": True, "end_to_end_raw_input": True, "contains_feature_engineering": True, "model_sha256": sha256_file(deploy_model), "schema_sha256": sha256_file(root / "models" / "input_schema.json"), "reload_predictions": reload_pred},
        "timing_seconds": {"full_training_run": duration, "final_fit_train_plus_validation": final_fit_s, "test_predict": final_predict_s},
        "input_schema_feature_count": schema["feature_count"],
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
