"""Cau hinh dung chung cho toan bo du an Ames Housing."""
from pathlib import Path

RANDOM_STATE = 42
TARGET = "SalePrice"
ID_COLUMN = "Id"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
EXPECTED_SPLIT_SHAPES = {
    "train": (1168, 81),
    "validation": (146, 81),
    "test": (146, 81),
}

# Cac cot thuc su la so trong bo Ames dang dung. MSSubClass co ma so nhung la category.
NUMERIC_COLUMNS = [
    "Id", "LotFrontage", "LotArea", "OverallQual", "OverallCond", "YearBuilt",
    "YearRemodAdd", "MasVnrArea", "BsmtFinSF1", "BsmtFinSF2", "BsmtUnfSF",
    "TotalBsmtSF", "1stFlrSF", "2ndFlrSF", "LowQualFinSF", "GrLivArea",
    "BsmtFullBath", "BsmtHalfBath", "FullBath", "HalfBath", "BedroomAbvGr",
    "KitchenAbvGr", "TotRmsAbvGrd", "Fireplaces", "GarageYrBlt", "GarageCars",
    "GarageArea", "WoodDeckSF", "OpenPorchSF", "EnclosedPorch", "3SsnPorch",
    "ScreenPorch", "PoolArea", "MiscVal", "MoSold", "YrSold", "SalePrice",
]

ENGINEERED_FEATURES = [
    "HouseAge", "RemodAge", "GarageAge", "TotalSF", "TotalBathrooms",
    "TotalPorchSF", "TotalOutdoorSF", "HasGarage", "HasBsmt", "HasFireplace",
    "HasPool", "Has2ndFloor", "HasMasVnr", "MoSold_sin", "MoSold_cos",
]
