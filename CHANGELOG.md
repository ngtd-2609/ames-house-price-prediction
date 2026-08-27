# CHANGELOG — Final Stability Round

Generated from the final-fix evidence set. This round intentionally preserves the canonical model, split, EDA outputs and Streamlit scope.

## 1. Testing
- Corrected official coverage semantics to explicit `src/house_price + backend` denominator.
- Baseline: **56 tests passed**, **84% true source coverage**; `tuning.py` and legacy `train.py` were at 0%.
- Added meaningful behavioral tests for tuning, reporting, artifacts, validation, prediction, backend and model-selection branches.
- Removed the dead `src/house_price/train.py` wrapper that inverted the intended dependency direction (`src -> scripts`).
- Final: **67 tests passed**, **99.9% source coverage** (706 statements, 1 missing) on `src/house_price + backend`.

## 2. Notebook
- Rebuilt Detailed notebook from **24 -> 27 cells** and Basic notebook from **8 -> 13 cells**.
- Development phase now loads only train/validation; `MODEL LOCKED` is emitted before the test dataframe/target is loaded.
- Added freshness validation for data hashes, model artifact hash, selected model/params, source fingerprint and generation time.
- Re-executed both notebooks from a clean kernel: Detailed **PASS**, Basic **PASS**, 0 execution errors.

## 3. Selection
- Synchronized `src/house_price/selection.py` and `outputs/model_selection_policy.json`.
- Executable rule is exactly: primary validation RMSE; Ridge may win only within **2%** validation tolerance and with CV RMSE mean no worse.
- `uses_test=false`; deployability/convergence/interpretability are not represented as executable criteria.
- Tuning candidates are explicitly predefined regularized linear candidates (ElasticNet and Ridge), matching implementation.

## 4. Consistency
- Replaced hard-coded test-count/coverage expectations in `scripts/check_project_consistency.py` with structured evidence reads.
- Checker computes SHA-256 of the canonical model directly and validates summary/metadata/policy.
- Checker parses notebooks, Markdown, DOCX and PPTX (including notes text) and checks actual test/coverage evidence freshness.
- Stale final-model claims are distinguished from legitimate benchmark mentions of candidate models.

## 5. Audit / documentation
- Deleted the previous `outputs/audit` generations (**45 old audit files**) and regenerated one canonical evidence set.
- README, Word, PDF, PPTX, QA/audit documents were synchronized to **67 tests / 99.9% source coverage**.
- Word was regenerated as A4 with a real TOC whose title “Mục lục” is not itself a TOC entry; visual render QA covered all 26 pages.
- PPTX remained a 20-slide flow, with updated selection/testing/reproducibility evidence and source notes.
- Assignment Excel was not edited; before/after SHA-256 is identical.
