import json, re
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from house_price.config import PROJECT_ROOT, TARGET, ID_COLUMN
from house_price.data import load_house_data, split_xy, sha256_file
from house_price.evaluation import regression_metrics, bootstrap_metric_ci
from house_price.validation import validate_splits
from house_price.artifacts import build_input_schema, load_model


def test_regression_metrics_and_bootstrap_ci_are_deterministic():
    y=np.array([100000,200000,300000], dtype=float)
    p=np.array([110000,190000,310000], dtype=float)
    m=regression_metrics(y,p)
    assert set(m)=={'RMSE','MAE','R2','RMSLE'} and m['RMSE']>0
    ci1=bootstrap_metric_ci(y,p,n_bootstrap=20,random_state=42)
    ci2=bootstrap_metric_ci(y,p,n_bootstrap=20,random_state=42)
    assert ci1==ci2 and ci1['n_bootstrap']==20


def test_protocol_source_has_model_lock_before_test_unlock():
    source=(PROJECT_ROOT/'scripts'/'train_full_project.py').read_text(encoding='utf-8')
    assert 'create_training_eda(train, validation, TABLES, FIGURES)' in source
    assert 'create_eda(train, validation, test)' not in source
    assert source.index('write_json(OUTPUT / \"model_selection_policy.json\", selection_policy)') < source.index('X_test, y_test = split_xy(test)')


def test_selection_policy_states_no_test_usage():
    policy=json.loads((PROJECT_ROOT/'outputs'/'model_selection_policy.json').read_text(encoding='utf-8'))
    assert policy['uses_test'] is False
    assert policy['locked_model']


def test_permutation_importance_has_real_repeats_and_nonzero_std():
    table=pd.read_csv(PROJECT_ROOT/'outputs'/'tables'/'permutation_importance.csv')
    measured=table[table['Repeats']>0]
    assert measured['Repeats'].min()>=20
    assert (measured['Importance_std'].fillna(0)>0).any()


def test_schema_policy_matches_backend_contract_words():
    schema=build_input_schema(load_house_data('house_train_80.csv'))
    policy=schema['policy']
    assert 'single_prediction_policy' in policy and 'batch_prediction_policy' in policy
    assert 'extra columns are preserved' in policy['extra_columns_policy']
    assert 'batch prediction rejects' in policy['missing_columns_policy']


def test_load_model_explicit_path_and_data_hash():
    model_path=PROJECT_ROOT/'models'/'house_price_pipeline.joblib'
    assert load_model(model_path) is not None
    assert len(sha256_file(model_path))==64


def test_validation_rejects_target_missing_and_schema_mismatch():
    tr=load_house_data('house_train_80.csv'); va=load_house_data('house_validation_10.csv'); te=load_house_data('house_test_10.csv')
    bad=tr.copy(); bad.loc[bad.index[0],TARGET]=np.nan
    with pytest.raises(ValueError): validate_splits(bad,va,te)
    bad2=te.drop(columns=[te.columns[-1]])
    with pytest.raises(ValueError): validate_splits(tr,va,bad2)


def test_split_xy_without_target_returns_none_y():
    tr=load_house_data('house_train_80.csv').drop(columns=[TARGET])
    X,y=split_xy(tr)
    assert y is None and ID_COLUMN not in X.columns


def test_no_duplicate_joblib_artifacts_remain():
    joblibs = sorted(PROJECT_ROOT.glob("**/*.joblib"))

    rel = [
        p.relative_to(PROJECT_ROOT).as_posix()
        for p in joblibs
    ]

    assert rel == ["models/house_price_pipeline.joblib"]