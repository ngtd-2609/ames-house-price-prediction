import json
import numpy as np
import pandas as pd
import pytest
from house_price.config import MODEL_DIR,OUTPUT_DIR
from house_price.data import load_house_data
from house_price.predict import prepare_raw_frame,predict_prices
from house_price.artifacts import load_model

def assets():
    model=load_model(); schema=json.loads((MODEL_DIR/'input_schema.json').read_text(encoding='utf-8')); return model,schema

def raw(n=3): return load_house_data('house_test_10.csv').drop(columns=['Id','SalePrice']).head(n)

def test_saved_pipeline_predicts_positive_finite_prices():
    m,s=assets(); p=predict_prices(m,raw(),s); assert len(p)==3 and (p>0).all() and np.isfinite(p).all()

def test_artifact_direct_predict_accepts_raw_without_external_feature_engineering():
    m,_=assets(); p=m.predict(raw(2)); assert len(p)==2 and np.isfinite(p).all()

def test_unknown_category_is_supported():
    m,s=assets(); X=raw(1).copy(); X.loc[X.index[0],'Neighborhood']='NEVER_SEEN_CATEGORY'; assert predict_prices(m,X,s)[0]>0

def test_missing_numeric_value_is_imputed():
    m,s=assets(); X=raw(1).copy(); X.loc[X.index[0],'LotFrontage']=np.nan; assert predict_prices(m,X,s)[0]>0

def test_bad_numeric_type_has_friendly_error():
    _,s=assets(); X=raw(1).copy(); X['LotArea']=X['LotArea'].astype('object'); X.loc[X.index[0],'LotArea']='not-a-number'
    with pytest.raises(ValueError,match='LotArea'): prepare_raw_frame(X,s)

def test_numeric_outside_train_domain_is_rejected():
    _,s=assets(); X=raw(1).copy(); X.loc[X.index[0],'OverallQual']=999
    with pytest.raises(ValueError,match='OverallQual'): prepare_raw_frame(X,s)

def test_empty_frame_is_rejected():
    _,s=assets();
    with pytest.raises(ValueError,match='khong co dong'): prepare_raw_frame(pd.DataFrame(),s)

def test_fixed_predictions_match_canonical_summary_tolerance():
    m,s=assets(); canonical=json.loads((OUTPUT_DIR/'summary.json').read_text(encoding='utf-8'))['artifact']['reload_predictions']; p=predict_prices(m,raw(3),s); assert np.allclose(p,canonical,rtol=0,atol=1e-6)
