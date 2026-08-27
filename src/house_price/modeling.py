"""Dinh nghia model va end-to-end estimator cho training/notebook/app."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import ElasticNet, LinearRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor

from .config import RANDOM_STATE
from .features import AmesFeatureEngineer
from .preprocessing import build_preprocessor


def model_definitions() -> dict[str, object]:
    """Bo model hop ly de so sanh; moi model cung mot pipeline va protocol."""
    return {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=10.0),
        "ElasticNet": ElasticNet(alpha=0.001, l1_ratio=0.2, max_iter=10000, tol=1e-3, random_state=RANDOM_STATE),
        "KNeighborsRegressor": KNeighborsRegressor(n_neighbors=7, weights="distance"),
        "DecisionTreeRegressor": DecisionTreeRegressor(max_depth=8, min_samples_leaf=5, random_state=RANDOM_STATE),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=20, max_features=0.8, min_samples_leaf=1,
            random_state=RANDOM_STATE, n_jobs=-1,
        ),
        "ExtraTreesRegressor": ExtraTreesRegressor(
            n_estimators=20, max_features=0.9, min_samples_leaf=1,
            random_state=RANDOM_STATE, n_jobs=-1,
        ),
        "GradientBoostingRegressor": GradientBoostingRegressor(
            n_estimators=30, learning_rate=0.05, max_depth=2,
            loss="huber", random_state=RANDOM_STATE,
        ),
        "HistGradientBoostingRegressor": HistGradientBoostingRegressor(
            max_iter=30, learning_rate=0.06, max_leaf_nodes=31,
            l2_regularization=1.0, random_state=RANDOM_STATE,
        ),
    }


def build_end_to_end_estimator(X_train_raw: pd.DataFrame, model) -> TransformedTargetRegressor:
    """Raw 79 features -> type/FE -> preprocessing -> regressor -> inverse log target."""
    preprocessor, _, _ = build_preprocessor(X_train_raw)
    pipeline = Pipeline([
        ("feature_engineering", AmesFeatureEngineer()),
        ("preprocessor", preprocessor),
        ("model", clone(model)),
    ])
    return TransformedTargetRegressor(
        regressor=pipeline,
        func=np.log1p,
        inverse_func=np.expm1,
        check_inverse=False,
    )


def tuning_space(name: str) -> dict[str, list]:
    spaces = {
        "Ridge": {"regressor__model__alpha": np.logspace(-1, 2, 12).tolist()},
        "ElasticNet": {
            "regressor__model__alpha": [0.001, 0.003, 0.01],
            "regressor__model__l1_ratio": [0.2, 0.5],
        },
        "KNeighborsRegressor": {
            "regressor__model__n_neighbors": list(range(3, 18, 2)),
            "regressor__model__weights": ["uniform", "distance"],
            "regressor__model__p": [1, 2],
        },
        "DecisionTreeRegressor": {
            "regressor__model__max_depth": [4, 6, 8, 10, 14, None],
            "regressor__model__min_samples_leaf": [1, 2, 4, 6, 10],
            "regressor__model__min_samples_split": [2, 5, 10, 20],
        },
        "RandomForestRegressor": {
            "regressor__model__n_estimators": [250, 350, 500],
            "regressor__model__max_depth": [None, 10, 16, 24],
            "regressor__model__max_features": ["sqrt", 0.5, 0.8, 1.0],
            "regressor__model__min_samples_leaf": [1, 2, 4],
        },
        "ExtraTreesRegressor": {
            "regressor__model__n_estimators": [250, 350, 500],
            "regressor__model__max_depth": [None, 10, 16, 24],
            "regressor__model__max_features": ["sqrt", 0.5, 0.8, 1.0],
            "regressor__model__min_samples_leaf": [1, 2, 4],
        },
        "GradientBoostingRegressor": {
            "regressor__model__n_estimators": [150, 250, 350, 500],
            "regressor__model__learning_rate": [0.02, 0.03, 0.05, 0.08],
            "regressor__model__max_depth": [2, 3],
            "regressor__model__min_samples_leaf": [3, 5, 10],
            "regressor__model__loss": ["huber", "squared_error"],
        },
        "HistGradientBoostingRegressor": {
            "regressor__model__learning_rate": [0.03, 0.06, 0.1],
            "regressor__model__max_leaf_nodes": [15, 31, 63],
            "regressor__model__l2_regularization": [0.0, 1.0, 5.0],
        },
    }
    if name == "LinearRegression":
        return {"regressor__model__fit_intercept": [True, False]}
    return spaces[name]
