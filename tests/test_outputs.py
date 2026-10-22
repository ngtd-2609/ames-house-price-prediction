import json
from pathlib import Path
from house_price.config import PROJECT_ROOT

def test_required_outputs_exist_and_are_nonzero():
    required=['outputs/summary.json','outputs/figures/06_split_distribution_check.png','outputs/tables/test_metrics.csv','models/house_price_pipeline.joblib','models/input_schema.json']
    for rel in required:
        p=PROJECT_ROOT/rel; assert p.exists() and p.stat().st_size>0, rel

def test_summary_and_training_summary_are_identical():
    a=json.loads((PROJECT_ROOT/'outputs/summary.json').read_text(encoding='utf-8')); b=json.loads((PROJECT_ROOT/'models/training_summary.json').read_text(encoding='utf-8')); assert a==b

def test_sample_batch_csv_contains_only_inputs_not_target():
    import pandas as pd
    df=pd.read_csv(PROJECT_ROOT/'data/house_input_sample.csv',keep_default_na=False); assert 'SalePrice' not in df.columns and len(df)>0

def test_streamlit_model_description_uses_canonical_model_name():
    json.loads((PROJECT_ROOT/'outputs/summary.json').read_text(encoding='utf-8'))
    for rel in ['app/Home.py','app/pages/3_Thong_tin_mo_hinh.py']:
        source=(PROJECT_ROOT/rel).read_text(encoding='utf-8')
        assert "selected_model" in source and "model_name" in source and "log-target Ridge" not in source
