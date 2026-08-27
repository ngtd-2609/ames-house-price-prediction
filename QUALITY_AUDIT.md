# QUALITY_AUDIT — Canonical Final Evidence

Generated: `2026-08-26T17:43:27.761243+00:00`

## Audit source of truth
- Canonical result: `outputs/summary.json`
- Canonical model metadata: `models/model_metadata.json`
- Test evidence: `outputs/audit/test_summary.json`
- Coverage evidence: `outputs/audit/coverage.json`
- Notebook evidence: `outputs/notebook_summary.json`
- Selection policy: `outputs/model_selection_policy.json`

## Current result
- Final model: **ElasticNet**
- Final params: `{"regressor__model__alpha": 0.001, "regressor__model__l1_ratio": 0.2}`
- Test RMSE: **22,228.60 USD**
- Validation RMSE: **24,855.66 USD**
- Tests: **67 passed**, 0 failed, 0 warnings in the canonical pytest run.
- Source coverage: **99.9%** (machine value `99.858356940510%`).
- Coverage scope: **`src/house_price + backend`**.
- Important modules with 0% coverage: **none**.

## Protocol checks
- Detailed notebook: **PASS**, 27 actual cells, test load after `MODEL LOCKED`.
- Basic notebook: **PASS**, 13 actual cells, test load after `MODEL LOCKED`.
- Policy code vs JSON: executable fields synchronized.
- Model preservation: **PASS**; model SHA before/after identical and fixed-sample prediction max absolute difference `0.0`.
- Assignment Excel: **PASS**; SHA before/after identical.

## Warning classification
The canonical normal pytest run reports **0 warnings**. A strict exploratory `pytest -W error` attempt surfaces a third-party seaborn/matplotlib deprecation path around the legacy EDA boxplot stack; it is not suppressed or counted as a project-code warning, and the final-fix scope does not alter EDA outputs merely to silence an upstream warning.

## Interpretation
Coverage is evidence, not a correctness proof. The final tests target behavior and branches that were previously weak (especially tuning/reporting/artifacts/validation/selection) rather than inflating the percentage through omit rules, mass `pragma: no cover`, or test-only denominator tricks.
