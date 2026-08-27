"""Data integrity checks cho ba split duoc cung cap."""
from __future__ import annotations

import pandas as pd
from .config import EXPECTED_SPLIT_SHAPES, ID_COLUMN, TARGET


def validate_splits(train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame) -> dict:
    frames = {"train": train, "validation": validation, "test": test}
    actual = {name: frame.shape for name, frame in frames.items()}
    if actual != EXPECTED_SPLIT_SHAPES:
        raise ValueError(f"Kich thuoc split khong dung: {actual}")
    if not (list(train.columns) == list(validation.columns) == list(test.columns)):
        raise ValueError("Schema cua ba split khong trung nhau")
    for name, frame in frames.items():
        if frame.duplicated().any():
            raise ValueError(f"Phat hien duplicate row trong {name}")
        if frame[ID_COLUMN].isna().any() or not frame[ID_COLUMN].is_unique:
            raise ValueError(f"Id trong {name} bi thieu hoac trung")
        if frame[TARGET].isna().any():
            raise ValueError(f"{TARGET} bi thieu trong {name}")
    id_sets = {name: set(frame[ID_COLUMN].tolist()) for name, frame in frames.items()}
    if (id_sets["train"] & id_sets["validation"] or id_sets["train"] & id_sets["test"]
            or id_sets["validation"] & id_sets["test"]):
        raise ValueError("Phat hien Id giao nhau giua cac split")
    ids = set().union(*id_sets.values())
    if len(ids) != sum(len(x) for x in id_sets.values()):
        raise ValueError("Tong Id khong duy nhat")
    return {
        "shapes": actual,
        "unique_ids": len(ids),
        "target": TARGET,
        "same_schema": True,
        "duplicate_rows": {name: int(frame.duplicated().sum()) for name, frame in frames.items()},
    }
