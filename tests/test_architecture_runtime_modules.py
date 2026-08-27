import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge

from house_price.config import PROJECT_ROOT
from house_price.data import load_house_data
from house_price.diagnostics import evaluate_locked_model
from house_price.eda import create_training_eda, data_dictionary, semantic_absence_mask
from house_price.reporting import (
    save_data_hashes,
    save_deployment_architecture_figure,
    save_feature_engineering_table,
    compute_cv_stability,
)
from house_price.modeling import build_end_to_end_estimator


def test_eda_helpers_create_tables_and_figures(tmp_path):
    train = load_house_data('house_train_80.csv').head(60).copy()
    val = load_house_data('house_validation_10.csv').head(30).copy()
    tables = tmp_path / 'tables'; figs = tmp_path / 'figures'
    stats, corr, missing = create_training_eda(train, val, tables, figs)
    assert stats['count'] == 60
    assert not corr.empty and not missing.empty
    assert (tables / 'data_dictionary.csv').exists()
    assert (figs / '01_target_distribution.png').stat().st_size > 0
    mask = semantic_absence_mask(pd.Series(['NA', 'None', '', 'x', None], dtype='object'))
    assert mask.tolist() == [True, True, True, False, True]
    assert 'Column' in data_dictionary(train).columns


def test_locked_model_diagnostics_write_expected_outputs(tmp_path):
    raw = load_house_data('house_test_10.csv').head(12).copy()
    X = raw.drop(columns=['Id','SalePrice'])
    y = raw['SalePrice']
    ids = raw['Id']
    estimator = DummyRegressor(strategy='mean').fit(X, y)
    tables = tmp_path / 'tables'; figs = tmp_path / 'figures'; tables.mkdir(); figs.mkdir()
    final, metrics, ci, preds, quartile, top_errors, importance, fit_s, pred_s = evaluate_locked_model(
        estimator, 'DummyRegressor', X.iloc[:6], y.iloc[:6], X.iloc[6:9], y.iloc[6:9], X.iloc[9:].copy(), y.iloc[9:].copy(), ids.iloc[9:].copy(), raw.iloc[9:].copy(), tables, figs
    )
    assert metrics['RMSE'] > 0
    assert ci['n_bootstrap'] == 300
    assert len(preds) == 3
    assert not quartile.empty
    assert not top_errors.empty
    assert (tables / 'permutation_importance.csv').exists()
    assert (figs / '12_permutation_importance.png').stat().st_size > 0
    assert fit_s >= 0 and pred_s >= 0


def test_reporting_helpers_write_artifacts(tmp_path):
    tables = tmp_path / 'tables'; figs = tmp_path / 'figures'; tables.mkdir(); figs.mkdir()
    hashes = save_data_hashes(PROJECT_ROOT, tables, ['house_train_80.csv'])
    assert len(hashes) == 1 and len(hashes[0]['sha256']) == 64
    save_feature_engineering_table(tables)
    assert (tables / 'feature_engineering.csv').exists()
    save_deployment_architecture_figure(figs, 'ElasticNet')
    assert (figs / '13_deployment_architecture.png').stat().st_size > 0


def test_compute_cv_stability_on_small_subset(tmp_path):
    train = load_house_data('house_train_80.csv').head(45).copy()
    X = train.drop(columns=['Id','SalePrice'])
    y = train['SalePrice']
    stability = compute_cv_stability(X, y, Ridge(alpha=1.0), {'regressor__model__alpha': 1.0}, tmp_path)
    assert stability['CV_RMSE_mean'] > 0
    assert (tmp_path / 'selected_model_cv_stability.csv').exists()
