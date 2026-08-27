"""Backend inference duy nhat cho Streamlit va test."""
from __future__ import annotations
import json, sys
from functools import lru_cache
from pathlib import Path
import joblib
import pandas as pd

PROJECT_ROOT=Path(__file__).resolve().parents[1]; SRC=PROJECT_ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from house_price.predict import predict_prices  # noqa: E402

MODEL_PATH=PROJECT_ROOT/'models'/'house_price_pipeline.joblib'
SCHEMA_PATH=PROJECT_ROOT/'models'/'input_schema.json'
SUMMARY_PATH=PROJECT_ROOT/'outputs'/'summary.json'

@lru_cache(maxsize=1)
def load_assets():
    """Load artifact mot lan moi process; khong fit/retrain."""
    if not MODEL_PATH.exists() or not SCHEMA_PATH.exists() or not SUMMARY_PATH.exists():
        raise FileNotFoundError('Thiếu model/schema/summary. Hãy chạy python scripts/train_full_project.py.')
    return (joblib.load(MODEL_PATH), json.loads(SCHEMA_PATH.read_text(encoding='utf-8')), json.loads(SUMMARY_PATH.read_text(encoding='utf-8')))

def predict_one(values: dict) -> float:
    model,schema,_=load_assets()
    return float(predict_prices(model,pd.DataFrame([values]),schema)[0])

def validate_batch_frame(frame: pd.DataFrame, schema: dict) -> None:
    if not isinstance(frame,pd.DataFrame): raise TypeError('Dữ liệu batch phải là DataFrame.')
    if frame.empty: raise ValueError('CSV không có dòng dữ liệu.')
    required=[f['name'] for f in schema['fields']]
    missing=sorted(set(required)-set(frame.columns))
    if missing: raise ValueError('CSV thiếu cột bắt buộc: '+', '.join(missing[:20])+(' ...' if len(missing)>20 else ''))

def predict_batch(frame: pd.DataFrame) -> pd.DataFrame:
    model,schema,_=load_assets(); validate_batch_frame(frame,schema)
    clean=frame.drop(columns=['SalePrice'],errors='ignore').copy()
    prediction_input=clean[[f['name'] for f in schema['fields']]]
    result=clean.copy(); result['PredictedSalePrice']=predict_prices(model,prediction_input,schema)
    return result
