# Reproducibility

## Environment

- Python requirement: >=3.11
- Actual audit Python: 3.13.5
- pandas: 2.2.3
- numpy: 2.3.5
- scikit-learn: 1.8.0
- random_state: 42

## Reproduce core outputs

```bash
pip install -r requirements.txt
python scripts/audit_data.py
python scripts/train_full_project.py
python scripts/build_metadata.py
python scripts/execute_notebooks.py
coverage erase
coverage run --source=src/house_price,backend -m pytest
coverage report -m
```

## Rebuild report and slides

```bash
python scripts/build_report.py
python scripts/build_slides.py
```

These scripts generate the DOCX/PDF/PPTX artifacts from canonical outputs rather than merely checking whether files exist.

## Canonical files

- `outputs/summary.json`
- `models/model_metadata.json`
- `outputs/model_selection_policy.json`
- `outputs/tables/data_hashes.csv`
- `models/house_price_pipeline.joblib`

## Current verification

- Pytest: 67 passed.
- Source coverage: 99.9% (`src/house_price + backend`).
- Structured evidence: `outputs/audit/test_summary.json`, `outputs/audit/coverage.json`.
- Streamlit: NOT VERIFIED IN CONTAINER - streamlit executable not available.


## Architecture refactor verification

The final architecture separates scientific logic from orchestration. `scripts/train_full_project.py` is now an orchestration entry point of about 145 lines with only `load_and_validate_project_data()` and `main()`. Reusable logic lives in `src/house_price`:

- `eda.py`: train/validation EDA only; no test target before model lock.
- `tuning.py`: validation benchmark and RandomizedSearchCV tuning.
- `selection.py`: executable `ModelSelectionPolicy` and `select_final_model()`.
- `diagnostics.py`: final post-lock test diagnostics and error tables.
- `explainability.py`: post-lock permutation importance with 20 repeats.
- `reporting.py`: summary, hashes, feature table, CV stability and artifact output.

Architecture tests in `tests/test_architecture_refactor.py` assert that the training script no longer defines the old large scientific functions and imports the refactored modules instead.


## Current canonical model

Final model: **ElasticNet**. Metrics and artifact hash are read from `outputs/summary.json` and `models/model_metadata.json`.
