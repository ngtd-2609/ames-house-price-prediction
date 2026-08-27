import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import ElasticNet, Ridge

from house_price import tuning
from house_price.artifacts import build_input_schema, load_model, save_input_schema
from house_price.config import PROJECT_ROOT, TARGET
from house_price.data import load_house_data, split_xy
from house_price.features import AmesFeatureEngineer, engineer_features
from house_price.modeling import model_definitions, tuning_space
from house_price.predict import predict_prices, prepare_raw_frame
from house_price.reporting import (
    build_summary_payload,
    save_canonical_artifact,
    write_json,
)
from house_price.selection import ModelSelectionPolicy, select_final_model
from house_price.validation import validate_splits
import backend.service as backend_service


def _raw(n=20):
    df = load_house_data("house_train_80.csv").head(n)
    return split_xy(df)


def _splits():
    return (
        load_house_data("house_train_80.csv"),
        load_house_data("house_validation_10.csv"),
        load_house_data("house_test_10.csv"),
    )


class _MeanEstimator:
    def fit(self, X, y):
        self.mean_ = float(np.mean(y))
        return self

    def predict(self, X):
        return np.full(len(X), self.mean_, dtype=float)


class _FakeSearch:
    def __init__(self, estimator, space, **kwargs):
        self.estimator = estimator
        self.space = space
        self.kwargs = kwargs

    def fit(self, X, y):
        self.best_estimator_ = _MeanEstimator().fit(X, y)
        self.best_index_ = 0
        first = {k: list(v)[0] for k, v in self.space.items()}
        self.best_params_ = first
        self.cv_results_ = {
            "mean_test_score": np.array([-10.0, -11.0]),
            "std_test_score": np.array([1.0, 1.5]),
            "mean_train_score": np.array([-9.0, -9.5]),
            "params": [first, first],
        }
        return self


def test_tuning_evaluate_candidates_real_logic_with_lightweight_estimator(tmp_path, monkeypatch):
    X, y = _raw(12)
    X_train, X_val = X.iloc[:8], X.iloc[8:]
    y_train, y_val = y.iloc[:8], y.iloc[8:]
    tables = tmp_path / "tables"; figures = tmp_path / "figures"
    tables.mkdir(); figures.mkdir()
    monkeypatch.setattr(tuning, "build_end_to_end_estimator", lambda X, definition: _MeanEstimator())
    results, fitted = tuning.evaluate_candidates(
        X_train, y_train, X_val, y_val, {"ToyModel": object()}, tables, figures
    )
    assert {"DummyRegressor (median)", "ToyModel"} <= set(results["Model"])
    assert "RMSE_gap" in results and "Relative_to_dummy_RMSE_improvement_pct" in results
    assert fitted["ToyModel"].mean_ == pytest.approx(float(y_train.mean()))
    assert (tables / "validation_model_comparison.csv").stat().st_size > 0
    assert (figures / "07_validation_model_comparison.png").stat().st_size > 0


def test_tune_candidates_cv_scoring_schema_and_determinism(tmp_path, monkeypatch):
    X, y = _raw(14)
    X_train, X_val = X.iloc[:10], X.iloc[10:]
    y_train, y_val = y.iloc[:10], y.iloc[10:]
    monkeypatch.setattr(tuning, "build_end_to_end_estimator", lambda X, definition: object())
    monkeypatch.setattr(tuning, "RandomizedSearchCV", _FakeSearch)
    defs = {"ElasticNet": ElasticNet(), "Ridge": Ridge()}
    table1, tuned1 = tuning.tune_candidates(defs, X_train, y_train, X_val, y_val, tmp_path)
    table2, _ = tuning.tune_candidates(defs, X_train, y_train, X_val, y_val, tmp_path)
    assert table1[["Model", "CV_RMSE_mean", "CV_RMSE_std", "Candidates_evaluated"]].equals(
        table2[["Model", "CV_RMSE_mean", "CV_RMSE_std", "Candidates_evaluated"]]
    )
    assert list(table1["Model"]) == ["ElasticNet (Tuned)", "Ridge (Tuned)"]
    assert set(tuned1) == {"ElasticNet", "Ridge"}
    assert set(["RMSE", "MAE", "R2", "RMSLE", "Search_seconds", "Best_params"]) <= set(table1.columns)
    assert (tmp_path / "tuning_results.csv").stat().st_size > 0


def test_tuning_rejects_unsupported_empty_candidate_set(tmp_path):
    X, y = _raw(8)
    with pytest.raises(ValueError, match="No supported tuning candidates"):
        tuning.tune_candidates({"LinearRegression": object()}, X, y, X, y, tmp_path)


def test_model_selection_full_policy_cases_and_invalid_inputs():
    base = pd.DataFrame([
        {"Model": "ElasticNet (Tuned)", "RMSE": 100.0, "CV_RMSE_mean": 110.0, "Best_params": "{}"},
        {"Model": "Ridge (Tuned)", "RMSE": 103.0, "CV_RMSE_mean": 100.0, "Best_params": '{"regressor__model__alpha": 1.0}'},
    ])
    selected, _, _ = select_final_model(base)
    assert selected == "ElasticNet"  # Ridge is outside 2% tolerance.

    within = base.copy(); within.loc[1, "RMSE"] = 101.0
    selected, _, payload = select_final_model(within)
    assert selected == "Ridge" and payload["uses_test"] is False
    assert payload["tie_breaker_order"] == ["validation_RMSE", "CV_RMSE_mean"]

    exact_tie = pd.DataFrame([
        {"Model": "Zed (Tuned)", "RMSE": 100.0, "CV_RMSE_mean": 100.0, "Best_params": "{}"},
        {"Model": "Alpha (Tuned)", "RMSE": 100.0, "CV_RMSE_mean": 100.0, "Best_params": "{}"},
    ])
    assert select_final_model(exact_tie)[0] == "Alpha"
    assert select_final_model(exact_tie)[0] == select_final_model(exact_tie.copy())[0]

    with pytest.raises(TypeError): select_final_model([])
    with pytest.raises(ValueError, match="empty"): select_final_model(pd.DataFrame())
    with pytest.raises(ValueError, match="missing required columns"): select_final_model(pd.DataFrame({"Model": ["A"]}))
    bad = base.copy(); bad.loc[0, "RMSE"] = np.nan
    with pytest.raises(ValueError, match="finite"): select_final_model(bad)
    with pytest.raises(ValueError, match="non-negative"):
        select_final_model(base, ModelSelectionPolicy(validation_tolerance=-0.1))
    malformed = base.copy(); malformed.loc[0, "Best_params"] = "not-json"
    with pytest.raises(ValueError, match="valid JSON"): select_final_model(malformed)
    scalar = base.copy(); scalar.loc[0, "Best_params"] = "1"
    with pytest.raises(ValueError, match="object"): select_final_model(scalar)


def test_policy_json_matches_code_defaults_and_locked_result():
    policy = json.loads((PROJECT_ROOT / "outputs/model_selection_policy.json").read_text(encoding="utf-8"))
    defaults = ModelSelectionPolicy()
    assert policy["primary_metric"] == defaults.primary_metric
    assert policy["validation_tolerance"] == defaults.validation_tolerance
    assert policy["ridge_tie_break_requires_cv_not_worse"] == defaults.ridge_tie_break_requires_cv_not_worse
    assert policy["uses_test"] is defaults.uses_test
    assert policy["candidate_filter"] == defaults.candidate_filter
    assert policy["tie_breaker_order"] == list(defaults.tie_breaker_order)


def test_validation_all_key_failure_branches_and_success():
    tr, va, te = _splits()
    out = validate_splits(tr, va, te)
    assert out["unique_ids"] == len(tr) + len(va) + len(te)

    wrong_shape = tr.iloc[:-1].copy()
    with pytest.raises(ValueError, match="Kich thuoc"):
        validate_splits(wrong_shape, va, te)

    schema_bad = va.rename(columns={va.columns[-1]: "DifferentColumn"})
    with pytest.raises(ValueError, match="Schema"):
        validate_splits(tr, schema_bad, te)

    dup = tr.copy(); dup.iloc[1] = dup.iloc[0]
    with pytest.raises(ValueError, match="duplicate row"):
        validate_splits(dup, va, te)

    dup_id = tr.copy(); dup_id.loc[dup_id.index[1], "Id"] = dup_id.loc[dup_id.index[0], "Id"]
    with pytest.raises(ValueError, match="Id"):
        validate_splits(dup_id, va, te)

    missing_target = tr.copy(); missing_target.loc[missing_target.index[0], TARGET] = np.nan
    with pytest.raises(ValueError, match=TARGET):
        validate_splits(missing_target, va, te)

    overlap = va.copy(); overlap.loc[overlap.index[0], "Id"] = tr.loc[tr.index[0], "Id"]
    with pytest.raises(ValueError, match="giao nhau"):
        validate_splits(tr, overlap, te)


def test_artifact_schema_save_and_model_default_path(tmp_path):
    tr = load_house_data("house_train_80.csv")
    schema = save_input_schema(tr, tmp_path)
    disk = json.loads((tmp_path / "input_schema.json").read_text(encoding="utf-8"))
    assert disk["feature_count"] == schema["feature_count"] == 79
    assert load_model() is not None


def test_feature_contract_and_prediction_error_branches():
    X, _ = _raw(3)
    missing = X.drop(columns=["YrSold"])
    with pytest.raises(ValueError, match="YrSold"):
        engineer_features(missing)
    with pytest.raises(TypeError):
        AmesFeatureEngineer().transform([[1, 2]])
    with pytest.raises(ValueError, match="input_features"):
        AmesFeatureEngineer().get_feature_names_out()
    names = AmesFeatureEngineer().get_feature_names_out(list(X.columns))
    assert "HouseAge" in names and "Id" not in names

    schema = build_input_schema(load_house_data("house_train_80.csv"))
    with pytest.raises(TypeError): prepare_raw_frame([], schema)
    partial = X[["OverallQual"]].copy()
    prepared = prepare_raw_frame(partial, schema)
    assert prepared.shape[1] == 79
    relaxed = partial.copy(); relaxed["OverallQual"] = "bad"
    prepared_relaxed = prepare_raw_frame(relaxed, schema, strict_numeric=False)
    assert prepared_relaxed["OverallQual"].isna().all()

    class BadModel:
        def predict(self, frame): return np.array([np.inf] * len(frame))
    with pytest.raises(ValueError, match="khong huu han"):
        predict_prices(BadModel(), partial, schema)


def test_reporting_serialization_summary_and_json(tmp_path):
    X, y = _raw(12)
    estimator = DummyRegressor(strategy="mean").fit(X, y)
    expected = pd.Series(estimator.predict(X))
    deploy_dir = tmp_path / "deploy"; out_dir = tmp_path / "out"; out_dir.mkdir()
    duplicate = out_dir / "best_house_price_model.joblib"; duplicate.write_bytes(b"old")
    duplicate2 = deploy_dir / "basic_ridge_pipeline.joblib"
    deploy_dir.mkdir(); duplicate2.write_bytes(b"old")
    model_path, reload_pred = save_canonical_artifact(estimator, deploy_dir, out_dir, X, expected)
    assert model_path.exists() and len(reload_pred) == 3
    assert not duplicate.exists() and not duplicate2.exists()

    bad_expected = expected.copy(); bad_expected.iloc[0] += 999
    with pytest.raises(AssertionError, match="differ"):
        save_canonical_artifact(estimator, tmp_path / "deploy2", out_dir, X, bad_expected)

    root = tmp_path / "root"
    (root / "scripts").mkdir(parents=True); (root / "src/house_price").mkdir(parents=True); (root / "models").mkdir()
    (root / "scripts/train_full_project.py").write_text("print('x')", encoding="utf-8")
    (root / "src/house_price/artifacts.py").write_text("# artifact", encoding="utf-8")
    (root / "models/input_schema.json").write_text("{}", encoding="utf-8")
    copied_model = root / "models/model.joblib"; copied_model.write_bytes(model_path.read_bytes())
    tr, va, te = _splits(); Xtr, _ = split_xy(tr)
    tiny = pd.DataFrame([{"a": 1}])
    payload = build_summary_payload(
        root, tr, va, te, Xtr, "ElasticNet", {"a": 1}, {"uses_test": False},
        {"RMSE": 1}, {"CV_RMSE_mean": 1}, {"RMSE": 2}, {"n_bootstrap": 1},
        {"count": 1}, tiny, tiny, tiny, tiny, tiny, tiny, tiny, [{"file": "x"}],
        copied_model, {"feature_count": 79}, [1.0, 2.0, 3.0], 1.0, 0.2, 0.1,
    )
    assert payload["selected_model"] == "ElasticNet"
    assert payload["dataset"]["input_features_raw"] == 79
    target = tmp_path / "payload.json"; write_json(target, payload)
    assert json.loads(target.read_text(encoding="utf-8"))["selected_model"] == "ElasticNet"


def test_backend_missing_assets_and_type_validation(monkeypatch, tmp_path):
    backend_service.load_assets.cache_clear()
    monkeypatch.setattr(backend_service, "MODEL_PATH", tmp_path / "missing-model")
    monkeypatch.setattr(backend_service, "SCHEMA_PATH", tmp_path / "missing-schema")
    monkeypatch.setattr(backend_service, "SUMMARY_PATH", tmp_path / "missing-summary")
    with pytest.raises(FileNotFoundError): backend_service.load_assets()
    with pytest.raises(TypeError): backend_service.validate_batch_frame([], {"fields": []})
    backend_service.load_assets.cache_clear()


def test_all_tuning_spaces_and_invalid_model_branch():
    defs = model_definitions()
    for name in defs:
        space = tuning_space(name)
        assert isinstance(space, dict) and space
    with pytest.raises(KeyError):
        tuning_space("NotAModel")
