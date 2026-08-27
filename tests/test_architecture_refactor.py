import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from house_price.config import PROJECT_ROOT
from house_price.explainability import permutation_importance_table
from house_price.selection import ModelSelectionPolicy, select_final_model
from house_price.diagnostics import prediction_error_tables


def test_training_script_is_orchestration_only_after_refactor():
    source = (PROJECT_ROOT / 'scripts' / 'train_full_project.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    assert funcs == ['load_and_validate_project_data', 'main']
    forbidden = ['def create_eda', 'def evaluate_candidates', 'def tune_candidates', 'def final_evaluation', 'permutation_importance(']
    for token in forbidden:
        assert token not in source
    assert 'from house_price.selection import' in source
    assert 'from house_price.tuning import' in source
    assert 'from house_price.diagnostics import' in source


def test_selection_policy_selects_ridge_only_when_rule_is_satisfied():
    table = pd.DataFrame([
        {'Model':'ElasticNet (Tuned)','RMSE':100.0,'CV_RMSE_mean':110.0,'Best_params':'{}'},
        {'Model':'Ridge (Tuned)','RMSE':101.0,'CV_RMSE_mean':109.0,'Best_params':'{"regressor__model__alpha": 10.0}'},
    ])
    selected, row, policy = select_final_model(table, ModelSelectionPolicy(validation_tolerance=0.02))
    assert selected == 'Ridge'
    assert row['Model'] == 'Ridge (Tuned)'
    assert policy['uses_test'] is False


def test_selection_policy_keeps_best_when_ridge_cv_is_worse():
    table = pd.DataFrame([
        {'Model':'ElasticNet (Tuned)','RMSE':100.0,'CV_RMSE_mean':105.0,'Best_params':'{}'},
        {'Model':'Ridge (Tuned)','RMSE':101.0,'CV_RMSE_mean':120.0,'Best_params':'{}'},
    ])
    selected, _, _ = select_final_model(table, ModelSelectionPolicy(validation_tolerance=0.02))
    assert selected == 'ElasticNet'


class LinearToyEstimator:
    def predict(self, X):
        return np.asarray(X['a'], dtype=float) * 10 + np.asarray(X['b'], dtype=float)


def test_permutation_importance_requires_real_repeat_count():
    X = pd.DataFrame({'a':[1,2,3,4,5,6], 'b':[10,10,10,10,10,10]})
    y = pd.Series([20,30,40,50,60,70], index=X.index, dtype=float)
    with pytest.raises(ValueError):
        permutation_importance_table(LinearToyEstimator(), X, y, repeats=3)
    table = permutation_importance_table(LinearToyEstimator(), X, y, repeats=20, sample_size=None, features=['a','b'])
    measured = table[table['Repeats'] > 0]
    assert measured['Repeats'].min() >= 20
    assert measured.loc[measured['Feature']=='a','Importance_std'].iloc[0] > 0


def test_prediction_error_tables_cover_quartile_and_groups():
    preds = pd.DataFrame({
        'Id':[1,2,3,4], 'ActualSalePrice':[100,200,300,400], 'PredictedSalePrice':[90,210,280,420]
    })
    preds['Residual'] = preds['ActualSalePrice'] - preds['PredictedSalePrice']
    preds['AbsoluteError'] = preds['Residual'].abs()
    preds['AbsolutePercentageError'] = preds['AbsoluteError'] / preds['ActualSalePrice'] * 100
    raw = pd.DataFrame({'Id':[1,2,3,4], 'Neighborhood':['A','A','A','A'], 'OverallQual':[5,6,7,8], 'GrLivArea':[900,1000,1100,1200], 'YearBuilt':[1990,1991,1992,1993]})
    quartile, top_errors, grouped = prediction_error_tables(preds, raw)
    assert len(quartile) == 4
    assert top_errors['AbsoluteError'].is_monotonic_decreasing
    assert {'Neighborhood','OverallQual'} <= set(grouped['GroupType'])
