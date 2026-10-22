import pandas as pd
import pytest
from backend.service import load_assets,predict_batch,predict_one,validate_batch_frame
from house_price.config import PROJECT_ROOT
from house_price.data import load_house_data

def batch(n=3): return load_house_data('house_test_10.csv').drop(columns=['SalePrice']).head(n)

def test_backend_load_assets_cached(): assert load_assets() is load_assets()

def test_predict_one_from_complete_raw_dict():
    row=batch(1).drop(columns=['Id']).iloc[0].to_dict(); assert predict_one(row)>0

def test_batch_preserves_row_count_and_id_and_adds_prediction():
    frame=batch(3); out=predict_batch(frame); assert len(out)==3 and out['Id'].tolist()==frame['Id'].tolist() and 'PredictedSalePrice' in out and 'SalePrice' not in out

def test_batch_accepts_extra_column_but_does_not_use_it():
    frame=batch(2); frame['Comment']='x'; out=predict_batch(frame); assert 'Comment' in out and len(out)==2

def test_batch_rejects_missing_required_column():
    _,schema,_=load_assets(); frame=batch(2).drop(columns=['OverallQual'])
    with pytest.raises(ValueError,match='OverallQual'): validate_batch_frame(frame,schema)

def test_batch_rejects_empty():
    _,schema,_=load_assets()
    with pytest.raises(ValueError,match='không có dòng|khong co dong'): validate_batch_frame(pd.DataFrame(),schema)

def test_downloadable_sample_csv_runs_end_to_end():
    frame=pd.read_csv(PROJECT_ROOT/'data'/'house_input_sample.csv',keep_default_na=False)
    out=predict_batch(frame)
    assert len(out)==len(frame) and out['PredictedSalePrice'].notna().all()
