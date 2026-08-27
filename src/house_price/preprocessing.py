"""Factory tien xu ly cho du lieu Ames sau feature engineering."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .features import engineer_features


def build_preprocessor(X_raw: pd.DataFrame) -> tuple[ColumnTransformer, list[str], list[str]]:
    engineered = engineer_features(X_raw)
    numeric = engineered.select_dtypes(include=np.number).columns.tolist()
    categorical = engineered.select_dtypes(exclude=np.number).columns.tolist()
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=2, sparse_output=False)),
    ])
    transformer = ColumnTransformer(
        [("numeric", numeric_pipe, numeric), ("categorical", categorical_pipe, categorical)],
        sparse_threshold=0,
        verbose_feature_names_out=False,
    )
    return transformer, numeric, categorical
