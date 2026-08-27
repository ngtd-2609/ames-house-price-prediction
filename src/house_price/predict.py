"""Validation va inference tu artifact end-to-end."""
from __future__ import annotations

import numpy as np
import pandas as pd


def prepare_raw_frame(frame: pd.DataFrame, schema: dict, *, strict_numeric: bool = True) -> pd.DataFrame:
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("Dau vao phai la pandas.DataFrame")
    if frame.empty:
        raise ValueError("Tep/du lieu dau vao khong co dong nao")
    defaults = {field["name"]: field["default"] for field in schema["fields"]}
    result = frame.copy()
    for name, value in defaults.items():
        if name not in result.columns:
            result[name] = value
    result = result[list(defaults)]
    for field in schema["fields"]:
        name = field["name"]
        if field["kind"] == "number":
            original_nonblank = result[name].notna() & (result[name].astype(str).str.strip() != "")
            converted = pd.to_numeric(result[name], errors="coerce")
            if strict_numeric and (original_nonblank & converted.isna()).any():
                bad = result.loc[original_nonblank & converted.isna(), name].astype(str).head(3).tolist()
                raise ValueError(f"Cot {name} co gia tri khong phai so: {bad}")
            min_value, max_value = field.get("min"), field.get("max")
            if min_value is not None and max_value is not None:
                invalid_range = converted.notna() & ((converted < min_value) | (converted > max_value))
                if invalid_range.any():
                    values = converted[invalid_range].head(3).tolist()
                    raise ValueError(f"Cot {name} nam ngoai mien train [{min_value}, {max_value}]: {values}")
            result[name] = converted
        else:
            # String unknown category duoc phep; OneHotEncoder(handle_unknown='ignore') xu ly.
            result[name] = result[name].fillna("Missing").astype(str)
    return result


def predict_prices(model, frame: pd.DataFrame, schema: dict) -> np.ndarray:
    """Artifact nhan raw input truc tiep; khong feature engineering ben ngoai model."""
    raw = prepare_raw_frame(frame, schema)
    prediction = np.asarray(model.predict(raw), dtype=float)
    if not np.isfinite(prediction).all():
        raise ValueError("Model tra ve gia tri khong huu han")
    return np.maximum(prediction, 0)
