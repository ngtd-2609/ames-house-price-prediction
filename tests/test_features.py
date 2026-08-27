import numpy as np
import pandas as pd
import pytest
from house_price.config import ENGINEERED_FEATURES
from house_price.data import load_house_data,split_xy
from house_price.features import AmesFeatureEngineer,coerce_feature_types,engineer_features

def raw(n=12):
    tr=load_house_data('house_train_80.csv'); X,_=split_xy(tr.head(n)); return X

def test_feature_engineering_is_row_preserving_target_free_and_complete():
    X=raw(); e=engineer_features(X); assert len(e)==len(X); assert 'SalePrice' not in e; assert set(ENGINEERED_FEATURES).issubset(e.columns)

def test_feature_engineering_keeps_raw_columns_and_is_deterministic():
    X=raw(); a=engineer_features(X); b=engineer_features(X); pd.testing.assert_frame_equal(a,b); assert set(X.columns).issubset(a.columns)

def test_age_features_never_negative_for_inconsistent_years():
    X=raw(1); X.loc[X.index[0],'YearBuilt']=2100; X.loc[X.index[0],'YearRemodAdd']=2100; X.loc[X.index[0],'GarageYrBlt']=2100
    e=engineer_features(X); assert (e[['HouseAge','RemodAge','GarageAge']].fillna(0)>=0).all().all()

def test_engineered_numeric_values_have_no_infinity():
    e=engineer_features(raw()); nums=e.select_dtypes(include=np.number); assert not np.isinf(nums.to_numpy(dtype=float)).any()

def test_transformer_matches_function():
    X=raw(); t=AmesFeatureEngineer().fit(X); pd.testing.assert_frame_equal(t.transform(X),engineer_features(X))

def test_transformer_rejects_non_dataframe():
    with pytest.raises(TypeError): AmesFeatureEngineer().fit([[1,2]])

def test_coerce_types_for_ms_subclass_and_numeric():
    X=raw(2).copy(); X['LotArea']=X['LotArea'].astype(str); out=coerce_feature_types(X); assert pd.api.types.is_numeric_dtype(out['LotArea']); assert out['MSSubClass'].dtype==object
