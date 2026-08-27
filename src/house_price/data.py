"""Doc du lieu va tao X/y ma khong lam mat semantic missing."""
from __future__ import annotations

import hashlib
from pathlib import Path
import pandas as pd

from .config import DATA_DIR, ID_COLUMN, NUMERIC_COLUMNS, TARGET


def resolve_data_path(path_or_name: str | Path) -> Path:
    path = Path(path_or_name)
    if not path.is_absolute() and not path.exists():
        path = DATA_DIR / path
    return path


def load_house_data(path_or_name: str | Path) -> pd.DataFrame:
    """Doc CSV; giu 'NA'/'None' o category va ep kieu dung cho cot numeric."""
    path = resolve_data_path(path_or_name)
    frame = pd.read_csv(path, encoding="utf-8-sig", keep_default_na=False)
    for column in NUMERIC_COLUMNS:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if "MSSubClass" in frame.columns:
        frame["MSSubClass"] = frame["MSSubClass"].astype(str)
    return frame


def split_xy(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series | None]:
    """Tach target va loai Id khoi tap dac trung de tranh hoc ma dinh danh."""
    y = frame[TARGET].copy() if TARGET in frame.columns else None
    drop_columns = [c for c in (TARGET, ID_COLUMN) if c in frame.columns]
    return frame.drop(columns=drop_columns), y


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
