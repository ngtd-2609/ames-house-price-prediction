# Architecture

## 1. Design goal

The project separates data science logic from notebooks, scripts and UI. The final artifact is an end-to-end pipeline that receives raw Ames-style input and returns predicted SalePrice in USD.

## 2. Training architecture

```text
CSV splits
  -> scripts/train_full_project.py orchestration
  -> src/house_price/data.py
  -> src/house_price/validation.py
  -> src/house_price/features.py
  -> src/house_price/preprocessing.py
  -> src/house_price/modeling.py
  -> src/house_price/evaluation.py
  -> src/house_price/artifacts.py
  -> outputs/summary.json + models/house_price_pipeline.joblib
```

## 3. Serving architecture

```text
User
  -> Streamlit pages under app/
  -> app/services/model_service.py
  -> backend/service.py
  -> models/house_price_pipeline.joblib
  -> prediction output
```

## 4. Pipeline boundary

The canonical artifact contains feature engineering and preprocessing. The app must not call `engineer_features()` separately and must not retrain the model.

## 5. Final estimator

Final estimator: **ElasticNet**. Hyperparameters: `{'regressor__model__l1_ratio': 0.2, 'regressor__model__alpha': 0.001}`.

## 6. Single source of truth

- Metrics: `outputs/summary.json`
- Artifact metadata: `models/model_metadata.json`
- Selection policy: `outputs/model_selection_policy.json`
- Core ML functions: `src/house_price/`

## 7. Leakage boundary

The code should follow train/validation development, model lock, and then test unlock. Documents and slides must match this timeline.


## Architecture refactor verification

The final architecture separates scientific logic from orchestration. `scripts/train_full_project.py` is now an orchestration entry point of about 145 lines with only `load_and_validate_project_data()` and `main()`. Reusable logic lives in `src/house_price`:

- `eda.py`: train/validation EDA only; no test target before model lock.
- `tuning.py`: validation benchmark and RandomizedSearchCV tuning.
- `selection.py`: executable `ModelSelectionPolicy` and `select_final_model()`.
- `diagnostics.py`: final post-lock test diagnostics and error tables.
- `explainability.py`: post-lock permutation importance with 20 repeats.
- `reporting.py`: summary, hashes, feature table, CV stability and artifact output.

Architecture tests in `tests/test_architecture_refactor.py` assert that the training script no longer defines the old large scientific functions and imports the refactored modules instead.
