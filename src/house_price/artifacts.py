"""Schema, artifact loading va metadata helpers."""
from __future__ import annotations

import json
from pathlib import Path
import joblib
import pandas as pd

from .config import ID_COLUMN, MODEL_DIR, TARGET

FIELD_DESCRIPTIONS = {
    "MSSubClass": ("Loại nhà theo mã xây dựng", "mã", "General"),
    "MSZoning": ("Khu vực quy hoạch", None, "General"),
    "LotFrontage": ("Chiều dài mặt tiền", "feet", "Location/Lot"),
    "LotArea": ("Diện tích lô đất", "ft²", "Location/Lot"),
    "Street": ("Loại đường tiếp cận", None, "Location/Lot"),
    "Alley": ("Loại hẻm tiếp cận", None, "Location/Lot"),
    "LotShape": ("Hình dạng lô đất", None, "Location/Lot"),
    "LandContour": ("Địa hình lô đất", None, "Location/Lot"),
    "Utilities": ("Tiện ích công cộng", None, "Amenities"),
    "LotConfig": ("Vị trí lô đất", None, "Location/Lot"),
    "LandSlope": ("Độ dốc lô đất", None, "Location/Lot"),
    "Neighborhood": ("Khu dân cư", None, "Location/Lot"),
    "Condition1": ("Điều kiện lân cận chính", None, "Location/Lot"),
    "Condition2": ("Điều kiện lân cận phụ", None, "Location/Lot"),
    "BldgType": ("Kiểu công trình", None, "Building"),
    "HouseStyle": ("Kiểu nhà", None, "Building"),
    "OverallQual": ("Chất lượng tổng thể", "thang 1-10", "Building"),
    "OverallCond": ("Tình trạng tổng thể", "thang 1-10", "Building"),
    "YearBuilt": ("Năm xây dựng", "năm", "Building"),
    "YearRemodAdd": ("Năm cải tạo gần nhất", "năm", "Building"),
    "RoofStyle": ("Kiểu mái", None, "Exterior"),
    "RoofMatl": ("Vật liệu mái", None, "Exterior"),
    "Exterior1st": ("Vật liệu ngoại thất chính", None, "Exterior"),
    "Exterior2nd": ("Vật liệu ngoại thất phụ", None, "Exterior"),
    "MasVnrType": ("Loại veneer xây", None, "Exterior"),
    "MasVnrArea": ("Diện tích veneer xây", "ft²", "Exterior"),
    "ExterQual": ("Chất lượng ngoại thất", None, "Exterior"),
    "ExterCond": ("Tình trạng ngoại thất", None, "Exterior"),
    "Foundation": ("Loại móng", None, "Basement"),
    "BsmtQual": ("Chiều cao/chất lượng tầng hầm", None, "Basement"),
    "BsmtCond": ("Tình trạng tầng hầm", None, "Basement"),
    "BsmtExposure": ("Mức tiếp xúc ngoài của tầng hầm", None, "Basement"),
    "BsmtFinType1": ("Loại hoàn thiện tầng hầm 1", None, "Basement"),
    "BsmtFinSF1": ("Diện tích tầng hầm hoàn thiện 1", "ft²", "Basement"),
    "BsmtFinType2": ("Loại hoàn thiện tầng hầm 2", None, "Basement"),
    "BsmtFinSF2": ("Diện tích tầng hầm hoàn thiện 2", "ft²", "Basement"),
    "BsmtUnfSF": ("Diện tích tầng hầm chưa hoàn thiện", "ft²", "Basement"),
    "TotalBsmtSF": ("Tổng diện tích tầng hầm", "ft²", "Basement"),
    "Heating": ("Loại hệ thống sưởi", None, "Amenities"),
    "HeatingQC": ("Chất lượng hệ thống sưởi", None, "Amenities"),
    "CentralAir": ("Điều hòa trung tâm", None, "Amenities"),
    "Electrical": ("Hệ thống điện", None, "Amenities"),
    "1stFlrSF": ("Diện tích tầng 1", "ft²", "Rooms"),
    "2ndFlrSF": ("Diện tích tầng 2", "ft²", "Rooms"),
    "LowQualFinSF": ("Diện tích hoàn thiện chất lượng thấp", "ft²", "Rooms"),
    "GrLivArea": ("Diện tích sinh hoạt trên mặt đất", "ft²", "Rooms"),
    "BsmtFullBath": ("Phòng tắm đầy đủ ở tầng hầm", "phòng", "Rooms"),
    "BsmtHalfBath": ("Phòng tắm nửa ở tầng hầm", "phòng", "Rooms"),
    "FullBath": ("Phòng tắm đầy đủ", "phòng", "Rooms"),
    "HalfBath": ("Phòng tắm nửa", "phòng", "Rooms"),
    "BedroomAbvGr": ("Số phòng ngủ trên mặt đất", "phòng", "Rooms"),
    "KitchenAbvGr": ("Số bếp trên mặt đất", "bếp", "Rooms"),
    "KitchenQual": ("Chất lượng bếp", None, "Rooms"),
    "TotRmsAbvGrd": ("Tổng số phòng trên mặt đất", "phòng", "Rooms"),
    "Functional": ("Mức độ sử dụng chức năng", None, "Rooms"),
    "Fireplaces": ("Số lò sưởi", "cái", "Amenities"),
    "FireplaceQu": ("Chất lượng lò sưởi", None, "Amenities"),
    "GarageType": ("Loại gara", None, "Garage"),
    "GarageYrBlt": ("Năm xây gara", "năm", "Garage"),
    "GarageFinish": ("Mức hoàn thiện gara", None, "Garage"),
    "GarageCars": ("Sức chứa gara", "số xe", "Garage"),
    "GarageArea": ("Diện tích gara", "ft²", "Garage"),
    "GarageQual": ("Chất lượng gara", None, "Garage"),
    "GarageCond": ("Tình trạng gara", None, "Garage"),
    "PavedDrive": ("Đường vào gara lát nhựa/bê tông", None, "Garage"),
    "WoodDeckSF": ("Diện tích sàn gỗ ngoài trời", "ft²", "Amenities"),
    "OpenPorchSF": ("Diện tích hiên mở", "ft²", "Amenities"),
    "EnclosedPorch": ("Diện tích hiên kín", "ft²", "Amenities"),
    "3SsnPorch": ("Diện tích hiên ba mùa", "ft²", "Amenities"),
    "ScreenPorch": ("Diện tích hiên lưới", "ft²", "Amenities"),
    "PoolArea": ("Diện tích hồ bơi", "ft²", "Amenities"),
    "PoolQC": ("Chất lượng hồ bơi", None, "Amenities"),
    "Fence": ("Chất lượng hàng rào", None, "Amenities"),
    "MiscFeature": ("Tiện ích phụ khác", None, "Amenities"),
    "MiscVal": ("Giá trị tiện ích phụ", "USD", "Amenities"),
    "MoSold": ("Tháng bán", "1-12", "Sale information"),
    "YrSold": ("Năm bán", "năm", "Sale information"),
    "SaleType": ("Loại giao dịch", None, "Sale information"),
    "SaleCondition": ("Điều kiện bán", None, "Sale information"),
}

CATEGORY_VALUE_HELP = {
    "Ex": "Excellent", "Gd": "Good", "TA": "Typical/Average", "Fa": "Fair", "Po": "Poor",
    "NA": "Không áp dụng/không có theo data dictionary", "None": "Không có", "Y": "Có", "N": "Không",
    "RL": "Residential Low Density", "RM": "Residential Medium Density", "FV": "Floating Village Residential", "RH": "Residential High Density", "C (all)": "Commercial",
}



def build_input_schema(frame: pd.DataFrame) -> dict:
    """Tao contract input tu TRAIN; khong dung test de tao default/domain."""
    features = frame.drop(columns=[TARGET, ID_COLUMN], errors="ignore")
    fields = []
    for column in features.columns:
        series = features[column]
        label, unit, group = FIELD_DESCRIPTIONS.get(column, (column, None, "Other"))
        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()
            fields.append({
                "name": column,
                "label": label,
                "description": label,
                "unit": unit,
                "group": group,
                "kind": "number",
                "default": float(clean.median()) if len(clean) else 0.0,
                "min": float(clean.min()) if len(clean) else 0.0,
                "max": float(clean.max()) if len(clean) else 0.0,
                "nullable": bool(series.isna().any()),
            })
        else:
            values = [str(v) for v in series.astype(str).value_counts(dropna=False).index.tolist()]
            fields.append({
                "name": column,
                "label": label,
                "description": label,
                "unit": unit,
                "group": group,
                "kind": "category",
                "default": values[0] if values else "Missing",
                "options": values,
                "option_labels": {v: CATEGORY_VALUE_HELP.get(v, v) for v in values},
                "nullable": False,
            })
    return {
        "target": TARGET,
        "id_excluded": True,
        "feature_count": len(fields),
        "policy": {
            "single_prediction_policy": "missing fields are filled with train-only defaults by prepare_raw_frame",
            "batch_prediction_policy": "CSV must contain all 79 required feature columns; SalePrice is dropped before prediction",
            "missing_columns_policy": "single prediction fills defaults; batch prediction rejects missing required feature columns with a friendly error",
            "extra_columns_policy": "extra columns are preserved in batch output but excluded from model input",
            "unknown_category_policy": "accepted by OneHotEncoder(handle_unknown='ignore')",
            "invalid_type_policy": "numeric parse failures are rejected with column-specific friendly errors",
            "range_policy": "numeric values outside train-observed min/max are rejected before prediction",
            "semantic_missing_policy": "NA/None tokens that encode absence are preserved as categories; true NaN in categorical fields becomes Missing",
        },
        "fields": fields,
    }


def save_input_schema(frame: pd.DataFrame, output_dir: str | Path = MODEL_DIR) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    schema = build_input_schema(frame)
    (output / "input_schema.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    return schema


def load_model(path: str | Path | None = None):
    return joblib.load(path or MODEL_DIR / "house_price_pipeline.joblib")
