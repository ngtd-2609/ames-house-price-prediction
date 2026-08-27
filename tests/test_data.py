import pandas as pd
import pytest
from house_price.config import ID_COLUMN,TARGET
from house_price.data import load_house_data,split_xy
from house_price.validation import validate_splits

def load_all(): return load_house_data('house_train_80.csv'),load_house_data('house_validation_10.csv'),load_house_data('house_test_10.csv')

def test_supplied_splits_have_expected_shape_and_unique_ids():
    tr,va,te=load_all(); result=validate_splits(tr,va,te); assert result['unique_ids']==1460 and result['same_schema']

def test_split_ids_are_pairwise_disjoint_and_unique():
    tr,va,te=load_all(); sets=[set(x[ID_COLUMN]) for x in (tr,va,te)]; assert not(sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2]); assert all(x[ID_COLUMN].is_unique for x in (tr,va,te))

def test_target_has_no_missing_and_is_not_in_X():
    tr,_,_=load_all(); X,y=split_xy(tr); assert TARGET not in X and ID_COLUMN not in X; assert y.notna().all()

def test_no_duplicate_rows():
    assert all(not f.duplicated().any() for f in load_all())

def test_na_none_tokens_are_preserved_as_categories():
    tr,_,_=load_all(); assert 'NA' in set(tr['PoolQC'].astype(str)); assert 'None' in set(tr['Alley'].astype(str)) or 'NA' in set(tr['Alley'].astype(str))

def test_ms_subclass_is_categorical_string():
    tr,_,_=load_all(); assert tr['MSSubClass'].dtype==object

def test_validation_rejects_duplicate_id():
    tr,va,te=load_all(); va=va.copy(); va.loc[va.index[0],ID_COLUMN]=tr.loc[tr.index[0],ID_COLUMN]
    with pytest.raises(ValueError,match='giao nhau|trung'): validate_splits(tr,va,te)
