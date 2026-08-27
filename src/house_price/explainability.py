"""Post-lock explainability diagnostics."""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import RANDOM_STATE
from .evaluation import regression_metrics
from .plotting import save_figure

DEFAULT_IMPORTANCE_FEATURES = [
    "OverallQual", "GrLivArea", "TotalBsmtSF", "GarageCars", "GarageArea", "YearBuilt", "YearRemodAdd", "1stFlrSF", "2ndFlrSF", "FullBath", "KitchenQual", "ExterQual", "Neighborhood", "LotArea", "Fireplaces",
]


def permutation_importance_table(final_estimator, X_test: pd.DataFrame, y_test: pd.Series, *, repeats: int = 20, sample_size: int | None = 50, random_state: int = RANDOM_STATE, features: list[str] | None = None) -> pd.DataFrame:
    """Compute raw-feature permutation importance after test unlock."""
    if repeats < 20:
        raise ValueError("Permutation importance requires at least 20 repeats for this project")
    rng = np.random.default_rng(random_state)
    n = len(X_test) if sample_size is None else min(sample_size, len(X_test))
    X_imp = X_test.sample(n=n, random_state=random_state).copy()
    y_imp = y_test.loc[X_imp.index].copy()
    base_rmse = regression_metrics(y_imp, final_estimator.predict(X_imp))["RMSE"]
    selected_features = [f for f in (features or DEFAULT_IMPORTANCE_FEATURES) if f in X_test.columns]
    rows: list[dict] = []
    for feature in selected_features:
        increases = []
        for _ in range(repeats):
            X_perm = X_imp.copy()
            X_perm[feature] = rng.permutation(X_perm[feature].to_numpy())
            increases.append(regression_metrics(y_imp, final_estimator.predict(X_perm))["RMSE"] - base_rmse)
        rows.append({"Feature": feature, "Importance_mean": float(np.mean(increases)), "Importance_std": float(np.std(increases, ddof=1)), "Repeats": repeats, "Sample_size": n})
    for feature in X_test.columns:
        if feature not in selected_features:
            rows.append({"Feature": feature, "Importance_mean": np.nan, "Importance_std": np.nan, "Repeats": 0, "Sample_size": n})
    return pd.DataFrame(rows).sort_values("Importance_mean", ascending=False, na_position="last").reset_index(drop=True)


def save_permutation_importance_plot(importance_table: pd.DataFrame, figures_dir) -> None:
    top_imp = importance_table.dropna().head(15).sort_values("Importance_mean")
    plt.figure(figsize=(8.5, 6))
    plt.barh(top_imp.Feature, top_imp.Importance_mean, xerr=top_imp.Importance_std)
    plt.title("Permutation importance sau model lock - test sample, 20 repeats")
    plt.xlabel("Mức tăng RMSE khi hoán vị (USD)")
    plt.ylabel("Raw feature")
    save_figure(figures_dir, "12_permutation_importance.png")
