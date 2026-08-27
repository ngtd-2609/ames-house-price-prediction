"""Feature engineering duy nhat cua du an."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from .config import ENGINEERED_FEATURES, ID_COLUMN, NUMERIC_COLUMNS, TARGET


def coerce_feature_types(frame: pd.DataFrame) -> pd.DataFrame:
    """Chuan hoa kieu du lieu tu raw Ames ma khong fit thong ke tu du lieu."""
    data = frame.copy()
    data = data.drop(columns=[c for c in (TARGET, ID_COLUMN) if c in data.columns], errors="ignore")
    numeric = set(NUMERIC_COLUMNS) - {TARGET, ID_COLUMN}
    for column in data.columns:
        if column in numeric:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    if "MSSubClass" in data.columns:
        data["MSSubClass"] = data["MSSubClass"].astype(str)
    return data


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Tao 15 dac trung theo tung dong; khong su dung target hay thong ke test."""
    data = coerce_feature_types(frame)
    required = {
        "YrSold", "YearBuilt", "YearRemodAdd", "GarageYrBlt", "TotalBsmtSF",
        "1stFlrSF", "2ndFlrSF", "FullBath", "HalfBath", "BsmtFullBath",
        "BsmtHalfBath", "WoodDeckSF", "OpenPorchSF", "EnclosedPorch",
        "3SsnPorch", "ScreenPorch", "PoolArea", "GarageArea", "Fireplaces",
        "MasVnrArea", "MoSold",
    }
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Thieu cot can cho feature engineering: {', '.join(missing)}")

    data["HouseAge"] = (data["YrSold"] - data["YearBuilt"]).clip(lower=0)
    data["RemodAge"] = (data["YrSold"] - data["YearRemodAdd"]).clip(lower=0)
    data["GarageAge"] = (data["YrSold"] - data["GarageYrBlt"]).clip(lower=0)
    data["TotalSF"] = data[["TotalBsmtSF", "1stFlrSF", "2ndFlrSF"]].sum(axis=1)
    data["TotalBathrooms"] = (
        data["FullBath"] + 0.5 * data["HalfBath"]
        + data["BsmtFullBath"] + 0.5 * data["BsmtHalfBath"]
    )
    porch = ["WoodDeckSF", "OpenPorchSF", "EnclosedPorch", "3SsnPorch", "ScreenPorch"]
    data["TotalPorchSF"] = data[porch].sum(axis=1)
    data["TotalOutdoorSF"] = data["TotalPorchSF"] + data["PoolArea"]
    data["HasGarage"] = (data["GarageArea"].fillna(0) > 0).astype(int)
    data["HasBsmt"] = (data["TotalBsmtSF"].fillna(0) > 0).astype(int)
    data["HasFireplace"] = (data["Fireplaces"].fillna(0) > 0).astype(int)
    data["HasPool"] = (data["PoolArea"].fillna(0) > 0).astype(int)
    data["Has2ndFloor"] = (data["2ndFlrSF"].fillna(0) > 0).astype(int)
    data["HasMasVnr"] = (data["MasVnrArea"].fillna(0) > 0).astype(int)
    data["MoSold_sin"] = np.sin(2 * np.pi * data["MoSold"] / 12)
    data["MoSold_cos"] = np.cos(2 * np.pi * data["MoSold"] / 12)
    return data


class AmesFeatureEngineer(BaseEstimator, TransformerMixin):
    """Sklearn-compatible transformer: raw Ames -> typed + engineered features."""

    def fit(self, X: pd.DataFrame, y=None):  # noqa: N803
        if not isinstance(X, pd.DataFrame):
            raise TypeError("AmesFeatureEngineer yeu cau dau vao pandas.DataFrame")
        # Validate contract during fit but learn no statistics.
        engineer_features(X.head(1) if len(X) else X)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:  # noqa: N803
        if not isinstance(X, pd.DataFrame):
            raise TypeError("AmesFeatureEngineer yeu cau dau vao pandas.DataFrame")
        return engineer_features(X)

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            raise ValueError("Can input_features de xac dinh ten dau ra")
        raw = [x for x in input_features if x not in {TARGET, ID_COLUMN}]
        return np.asarray(raw + ENGINEERED_FEATURES, dtype=object)
