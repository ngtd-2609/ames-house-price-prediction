"""Final holdout diagnostics after model lock."""
from __future__ import annotations

import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.base import clone

from .config import ID_COLUMN
from .evaluation import bootstrap_metric_ci, regression_metrics
from .explainability import permutation_importance_table, save_permutation_importance_plot
from .plotting import save_figure


def prediction_error_tables(predictions: pd.DataFrame, raw_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create quartile, top-error and grouped error tables."""
    predictions = predictions.copy()
    predictions["PriceQuartile"] = pd.qcut(predictions.ActualSalePrice, 4, labels=["Q1 - thấp", "Q2", "Q3", "Q4 - cao"])
    quartile = predictions.groupby("PriceQuartile", observed=True).agg(Count=("Id", "size"), MAE=("AbsoluteError", "mean"), Median_AE=("AbsoluteError", "median"), MAPE=("AbsolutePercentageError", "mean")).reset_index()
    error_detail = predictions.merge(raw_test[[ID_COLUMN, "Neighborhood", "OverallQual", "GrLivArea", "YearBuilt"]], on="Id", how="left")
    top_errors = error_detail.sort_values("AbsoluteError", ascending=False).head(10)
    neighborhood = error_detail.groupby("Neighborhood").agg(Count=("Id", "size"), MAE=("AbsoluteError", "mean"), MAPE=("AbsolutePercentageError", "mean")).query("Count >= 3").sort_values("MAE", ascending=False).reset_index()
    quality = error_detail.groupby("OverallQual").agg(Count=("Id", "size"), MAE=("AbsoluteError", "mean"), MAPE=("AbsolutePercentageError", "mean")).reset_index()
    return quartile, top_errors, pd.concat({"Neighborhood": neighborhood, "OverallQual": quality}, names=["GroupType"]).reset_index(level=0)


def evaluate_locked_model(selected_estimator, selected_name: str, X_train, y_train, X_val, y_val, X_test, y_test, ids_test, raw_test, tables_dir, figures_dir):
    """Fit selected model on train+validation and evaluate final holdout test."""
    X_train_val = pd.concat([X_train, X_val], ignore_index=True)
    y_train_val = pd.concat([y_train, y_val], ignore_index=True)
    final_estimator = clone(selected_estimator)
    start = time.perf_counter()
    final_estimator.fit(X_train_val, y_train_val)
    fit_seconds = time.perf_counter() - start
    start = time.perf_counter()
    test_pred = np.maximum(final_estimator.predict(X_test), 0)
    predict_seconds = time.perf_counter() - start
    metrics = regression_metrics(y_test, test_pred)
    ci = bootstrap_metric_ci(y_test, test_pred, n_bootstrap=300)
    pd.DataFrame([{ "Model": f"{selected_name} (Tuned)", **metrics,
        "RMSE_CI95_low": ci["RMSE_95CI"]["lower"], "RMSE_CI95_high": ci["RMSE_95CI"]["upper"],
        "MAE_CI95_low": ci["MAE_95CI"]["lower"], "MAE_CI95_high": ci["MAE_95CI"]["upper"],
    }]).to_csv(tables_dir / "test_metrics.csv", index=False, encoding="utf-8-sig")

    predictions = pd.DataFrame({"Id": ids_test.to_numpy(), "ActualSalePrice": y_test.to_numpy(), "PredictedSalePrice": test_pred})
    predictions["Residual"] = predictions["ActualSalePrice"] - predictions["PredictedSalePrice"]
    predictions["AbsoluteError"] = predictions["Residual"].abs()
    predictions["AbsolutePercentageError"] = predictions["AbsoluteError"] / predictions["ActualSalePrice"] * 100
    predictions.to_csv(tables_dir / "test_predictions.csv", index=False, encoding="utf-8-sig")

    lower = min(predictions.ActualSalePrice.min(), predictions.PredictedSalePrice.min())
    upper = max(predictions.ActualSalePrice.max(), predictions.PredictedSalePrice.max())
    plt.figure(figsize=(6.4, 5.4))
    sns.scatterplot(data=predictions, x="ActualSalePrice", y="PredictedSalePrice", alpha=0.7, color="#2F75B5")
    plt.plot([lower, upper], [lower, upper], "--", label="Dự báo hoàn hảo")
    plt.title("Giá thực tế và giá dự báo - test")
    plt.xlabel("Giá thực tế (USD)")
    plt.ylabel("Giá dự báo (USD)")
    plt.legend()
    save_figure(figures_dir, "08_actual_vs_predicted.png")

    plt.figure(figsize=(6.4, 5.0))
    sns.scatterplot(data=predictions, x="PredictedSalePrice", y="Residual", alpha=0.7, color="#4472C4")
    plt.axhline(0, linestyle="--")
    plt.title("Residual theo giá dự báo - test")
    plt.xlabel("Giá dự báo (USD)")
    plt.ylabel("Residual: thực tế - dự báo (USD)")
    save_figure(figures_dir, "09_residual_vs_predicted.png")

    plt.figure(figsize=(6.4, 4.8))
    sns.histplot(predictions.Residual, kde=True, color="#5B9BD5")
    plt.axvline(0, linestyle="--")
    plt.title("Phân phối residual - test")
    plt.xlabel("Residual (USD)")
    plt.ylabel("Số căn nhà")
    save_figure(figures_dir, "10_residual_distribution.png")

    quartile, top_errors, grouped_errors = prediction_error_tables(predictions, raw_test)
    quartile.to_csv(tables_dir / "error_by_price_quartile.csv", index=False, encoding="utf-8-sig")
    top_errors.to_csv(tables_dir / "top10_absolute_errors.csv", index=False, encoding="utf-8-sig")
    grouped_errors[grouped_errors["GroupType"] == "Neighborhood"].drop(columns=["GroupType"]).to_csv(tables_dir / "error_by_neighborhood.csv", index=False, encoding="utf-8-sig")
    grouped_errors[grouped_errors["GroupType"] == "OverallQual"].drop(columns=["GroupType"]).to_csv(tables_dir / "error_by_overall_quality.csv", index=False, encoding="utf-8-sig")

    plt.figure(figsize=(7, 4.8))
    sns.barplot(data=quartile, x="PriceQuartile", y="MAE", color="#ED7D31")
    plt.title("MAE theo nhóm giá thực tế - test")
    plt.xlabel("Nhóm giá")
    plt.ylabel("MAE (USD)")
    save_figure(figures_dir, "11_error_by_price_quartile.png")

    print("PERMUTATION_IMPORTANCE_START", flush=True)
    importance_table = permutation_importance_table(final_estimator, X_test, y_test, repeats=20, sample_size=50)
    importance_table.to_csv(tables_dir / "permutation_importance.csv", index=False, encoding="utf-8-sig")
    save_permutation_importance_plot(importance_table, figures_dir)
    print("PERMUTATION_IMPORTANCE_DONE", flush=True)
    return final_estimator, metrics, ci, predictions, quartile, top_errors, importance_table, fit_seconds, predict_seconds
