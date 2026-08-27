"""EDA and data-description outputs for the house price project.

This module deliberately uses only train/validation inputs. Test target is not
accepted here so the training script cannot accidentally use holdout labels
before model lock.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from .config import TARGET
from .plotting import save_figure


def semantic_absence_mask(series: pd.Series) -> pd.Series:
    """Return true missing plus domain semantic absence tokens for reporting."""
    mask = series.isna()
    if series.dtype == "object":
        mask = mask | series.isin(["NA", "None", ""])
    return mask


def data_dictionary(train: pd.DataFrame) -> pd.DataFrame:
    """Create a compact data dictionary from the training split only."""
    rows: list[dict] = []
    for column in train.columns:
        series = train[column]
        absence = semantic_absence_mask(series)
        rows.append({
            "Column": column,
            "Dtype": str(series.dtype),
            "Unique": int(series.nunique(dropna=False)),
            "Missing_or_absence_count": int(absence.sum()),
            "Missing_or_absence_pct": float(absence.mean() * 100),
            "Examples": ", ".join(str(v) for v in series.drop_duplicates().head(3).tolist()),
        })
    return pd.DataFrame(rows)


def create_training_eda(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    tables_dir: Path,
    figures_dir: Path,
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Generate EDA artifacts without accessing the test target."""
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    dictionary = data_dictionary(train)
    dictionary.to_csv(tables_dir / "data_dictionary.csv", index=False, encoding="utf-8-sig")

    target_stats = {
        "count": int(train[TARGET].count()),
        "mean": float(train[TARGET].mean()),
        "median": float(train[TARGET].median()),
        "std": float(train[TARGET].std()),
        "min": float(train[TARGET].min()),
        "q1": float(train[TARGET].quantile(0.25)),
        "q3": float(train[TARGET].quantile(0.75)),
        "q95": float(train[TARGET].quantile(0.95)),
        "max": float(train[TARGET].max()),
        "skewness": float(train[TARGET].skew()),
        "log1p_skewness": float(np.log1p(train[TARGET]).skew()),
    }
    # Phân phối biến mục tiêu SalePrice.
    # Dùng định dạng nghìn USD để tránh các tick 100000, 200000, ...
    # bị chồng chữ khi hiển thị trong notebook/report.

    from matplotlib.ticker import FuncFormatter, MaxNLocator

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(16, 4.8),
        gridspec_kw={"width_ratios": [1.15, 1.0, 1.15]},
    )

    # Formatter: 100000 -> 100k, 250000 -> 250k
    usd_thousands = FuncFormatter(
        lambda value, position: f"{value / 1000:.0f}k"
    )

    # --- 1. Phân phối SalePrice gốc ---
    sns.histplot(
        train[TARGET],
        kde=True,
        bins=30,
        ax=axes[0],
        color="#2F75B5",
        edgecolor="white",
        linewidth=0.5,
    )

    axes[0].set_title(
        "Phân phối SalePrice",
        fontsize=12,
        pad=10,
    )
    axes[0].set_xlabel("Giá bán (nghìn USD)")
    axes[0].set_ylabel("Số căn nhà")

    axes[0].xaxis.set_major_formatter(usd_thousands)
    axes[0].xaxis.set_major_locator(MaxNLocator(nbins=7))

    axes[0].tick_params(
        axis="x",
        labelsize=9,
    )
    axes[0].grid(
        axis="y",
        alpha=0.2,
    )

    # --- 2. Phân phối sau log1p ---
    log_target = np.log1p(train[TARGET])

    sns.histplot(
        log_target,
        kde=True,
        bins=30,
        ax=axes[1],
        color="#70AD47",
        edgecolor="white",
        linewidth=0.5,
    )

    axes[1].set_title(
        "Phân phối log1p(SalePrice)",
        fontsize=12,
        pad=10,
    )
    axes[1].set_xlabel("log(1 + SalePrice)")
    axes[1].set_ylabel("Số căn nhà")

    axes[1].xaxis.set_major_locator(MaxNLocator(nbins=7))
    axes[1].tick_params(
        axis="x",
        labelsize=9,
    )
    axes[1].grid(
        axis="y",
        alpha=0.2,
    )

    # --- 3. Boxplot SalePrice ---
    sns.boxplot(
        x=train[TARGET],
        ax=axes[2],
        color="#A9C4E4",
        width=0.45,
    )

    axes[2].set_title(
        "Boxplot SalePrice",
        fontsize=12,
        pad=10,
    )
    axes[2].set_xlabel("Giá bán (nghìn USD)")
    axes[2].set_ylabel("")

    axes[2].xaxis.set_major_formatter(usd_thousands)
    axes[2].xaxis.set_major_locator(MaxNLocator(nbins=7))

    axes[2].tick_params(
        axis="x",
        labelsize=9,
    )

    fig.suptitle(
        "Phân phối biến mục tiêu trước và sau biến đổi log",
        fontsize=14,
        fontweight="bold",
        y=1.03,
    )

    fig.subplots_adjust(
        wspace=0.22,
    )

    save_figure(
        figures_dir,
        "01_target_distribution.png",
    )

    missing = dictionary[["Column", "Missing_or_absence_count", "Missing_or_absence_pct"]].sort_values("Missing_or_absence_pct", ascending=False).head(20)
    missing.to_csv(tables_dir / "missingness_top20.csv", index=False, encoding="utf-8-sig")
    plt.figure(figsize=(9, 6))
    sns.barplot(data=missing, y="Column", x="Missing_or_absence_pct", color="#5B9BD5")
    plt.title("20 biến có tỷ lệ thiếu/không áp dụng cao nhất - train")
    plt.xlabel("Tỷ lệ (%)")
    plt.ylabel("Biến")
    save_figure(figures_dir, "02_missingness_top20.png")

    numeric_train = train.select_dtypes(include=np.number)
    corr = numeric_train.corr(numeric_only=True)[TARGET].drop(TARGET).sort_values(key=lambda s: s.abs(), ascending=False)
    corr_table = corr.rename("Correlation_with_SalePrice").rename_axis("Feature").reset_index()
    corr_table.to_csv(tables_dir / "numeric_correlations.csv", index=False, encoding="utf-8-sig")
    plt.figure(figsize=(8.5, 5.8))
    sns.barplot(data=corr_table.head(15), y="Feature", x="Correlation_with_SalePrice", color="#4472C4")
    plt.title("15 biến số tương quan mạnh nhất với SalePrice")
    plt.xlabel("Hệ số tương quan Pearson (không hàm ý nhân quả)")
    plt.ylabel("Biến")
    save_figure(figures_dir, "03_top_numeric_correlations.png")

    scatter_features = ["OverallQual", "GrLivArea", "GarageCars", "GarageArea", "TotalBsmtSF", "1stFlrSF"]
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    for axis, feature in zip(axes.ravel(), scatter_features):
        sns.regplot(data=train, x=feature, y=TARGET, scatter_kws={"alpha": 0.42, "s": 14, "color": "#5B9BD5"}, line_kws={"linewidth": 1.3, "color": "#C00000"}, ax=axis)
        axis.set_title(f"{feature} và SalePrice")
        axis.set_ylabel("SalePrice (USD)")
    save_figure(figures_dir, "04_numeric_relationships.png")

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    for axis, feature in zip(axes.ravel(), ["Neighborhood", "ExterQual", "KitchenQual", "GarageFinish"]):
        order = train.groupby(feature, dropna=False)[TARGET].median().sort_values().index
        sns.boxplot(data=train, x=feature, y=TARGET, order=order, ax=axis, fliersize=1.5, color="#B4C7E7")
        axis.tick_params(axis="x", rotation=65 if feature == "Neighborhood" else 0)
        axis.set_title(f"SalePrice theo {feature}")
        axis.set_xlabel(feature)
        axis.set_ylabel("SalePrice (USD)")
    save_figure(figures_dir, "05_categorical_relationships.png")

    compare_features = [TARGET, "OverallQual", "GrLivArea", "GarageCars", "TotalBsmtSF", "YearBuilt"]
    pieces = []
    for name, frame in [("Train", train), ("Validation", validation)]:
        temp = frame[compare_features].copy()
        temp["Split"] = name
        pieces.append(temp)
    split_compare = pd.concat(pieces, ignore_index=True)
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5))
    for axis, feature in zip(axes.ravel(), compare_features):
        sns.boxplot(data=split_compare, x="Split", y=feature, ax=axis, fliersize=1.5, color="#D9E2F3")
        axis.set_title(f"Phân phối {feature}")
        axis.set_xlabel("Tập dữ liệu")
        axis.set_ylabel("USD" if feature == TARGET else feature)
    save_figure(figures_dir, "06_split_distribution_check.png")

    drift_rows = []
    for feature in ["OverallQual", "GrLivArea", "GarageCars", "TotalBsmtSF", "YearBuilt", TARGET]:
        train_mean = float(train[feature].mean())
        train_std = float(train[feature].std()) or 1.0
        for split_name, frame in [("Validation", validation)]:
            mean = float(frame[feature].mean())
            smd = (mean - train_mean) / train_std
            drift_rows.append({"Feature": feature, "Split": split_name, "Train_mean": train_mean, "Split_mean": mean, "Standardized_mean_difference": smd, "Flag_abs_gt_0_2": abs(smd) > 0.2})
    drift = pd.DataFrame(drift_rows)
    drift.to_csv(tables_dir / "split_drift_numeric.csv", index=False, encoding="utf-8-sig")
    return target_stats, corr_table, missing
