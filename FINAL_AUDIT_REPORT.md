# FINAL_AUDIT_REPORT

Generated from the canonical evidence set. This report is regenerated rather than patched from the previous audit.

## 1. Scope
This final-fix round addresses exactly five technical groups: (1) real source testing/coverage for `src/house_price + backend`; (2) notebook source/model-lock/freshness; (3) executable model-selection policy consistency; (4) an evidence-driven consistency checker; and (5) stale-audit removal plus synchronized README/Word/PDF/PPTX/audit regeneration. Model replacement, resplitting, EDA redesign and Streamlit deployment are outside this round.

## 2. Model preservation
| Evidence | Before | After | Status |
|---|---|---|---|
| Final model | `ElasticNet` | `ElasticNet` | PASS |
| Params | `{"regressor__model__alpha": 0.001, "regressor__model__l1_ratio": 0.2}` | `{"regressor__model__alpha": 0.001, "regressor__model__l1_ratio": 0.2}` | PASS |
| Model SHA-256 | `5101114637e8001c91f06a42737cd3cc8ee143cb1d6a3a27631a41b48f3efcf1` | `5101114637e8001c91f06a42737cd3cc8ee143cb1d6a3a27631a41b48f3efcf1` | PASS |
| Validation RMSE | 24,855.66 | 24,855.66 | PASS |
| Test RMSE | 22,228.60 | 22,228.60 | PASS |
| Fixed-sample prediction max abs diff | - | `0.0` | **PASS** |

Canonical final model: **ElasticNet**. Canonical test RMSE: **22,228.60 USD**.

## 3. Testing
- Tests passed: **67**
- Tests failed: **0**
- Tests skipped: **0**
- Canonical pytest warnings: **0**
- Source coverage: **99.9%** (machine value `99.858356940510%`)
- **Coverage scope = `src/house_price + backend`**
- Baseline evidence before the final fix: 56 passed, 84% true source coverage.

## 4. Module coverage
| Module | Statements | Missing | Coverage |
|---|---:|---:|---:|
| `backend/__init__.py` | 2 | 0 | 100.0% |
| `backend/service.py` | 32 | 0 | 100.0% |
| `src/house_price/__init__.py` | 4 | 0 | 100.0% |
| `src/house_price/artifacts.py` | 28 | 0 | 100.0% |
| `src/house_price/config.py` | 11 | 0 | 100.0% |
| `src/house_price/data.py` | 29 | 0 | 100.0% |
| `src/house_price/diagnostics.py` | 81 | 0 | 100.0% |
| `src/house_price/eda.py` | 102 | 0 | 100.0% |
| `src/house_price/evaluation.py` | 22 | 0 | 100.0% |
| `src/house_price/explainability.py` | 39 | 0 | 100.0% |
| `src/house_price/features.py` | 53 | 0 | 100.0% |
| `src/house_price/modeling.py` | 24 | 0 | 100.0% |
| `src/house_price/plotting.py` | 10 | 0 | 100.0% |
| `src/house_price/predict.py` | 37 | 0 | 100.0% |
| `src/house_price/preprocessing.py` | 16 | 0 | 100.0% |
| `src/house_price/reporting.py` | 67 | 0 | 100.0% |
| `src/house_price/selection.py` | 54 | 0 | 100.0% |
| `src/house_price/tuning.py` | 71 | 0 | 100.0% |
| `src/house_price/validation.py` | 24 | 1 | 95.8% |

No important production module has 0% coverage. `tuning.py`, `reporting.py`, `artifacts.py` and `backend/service.py` are at 100%; `validation.py` is above 95%.

## 5. Notebook
- Detailed: **PASS**, 27 actual cells, 15 code cells, 0 execution errors.
- Basic: **PASS**, 13 actual cells, 8 code cells, 0 execution errors.
- Protocol: train/validation development -> model selection -> **MODEL LOCKED** -> test load/target -> final evaluation.
- Freshness gate: data hashes, model artifact hash, selected model/params, source fingerprint and generation metadata are validated before stale outputs are trusted.
- Notebook summary is generated from the actual notebook files, not a hard-coded cell count.

## 6. Selection policy
- Primary metric: `validation_RMSE`.
- Validation tolerance: `0.02`.
- Ridge tie-break requires CV no worse: `True`.
- Uses test during selection: `False`.
- Tie-break order: `['validation_RMSE', 'CV_RMSE_mean']`.
- Candidate design: `Predefined tuned candidates: ElasticNet and Ridge; test is unavailable during selection.`.
- Code defaults vs `outputs/model_selection_policy.json`: **PASS by unit test and consistency checker design**.
- Deployment simplicity/interpretability/convergence are qualitative considerations only; they are not misrepresented as executable selection criteria.

## 7. Consistency
`scripts/check_project_consistency.py` now derives truth from structured current evidence instead of expecting strings such as an old test count or coverage. It computes model SHA-256 directly, validates metadata/summary/policy, reads structured pytest/coverage evidence, opens actual notebooks, parses Markdown, parses DOCX with `python-docx`, and parses PPTX + notes with `python-pptx`. A failing check exits nonzero.

Final checker result is recorded in `outputs/audit/consistency_final.txt`; the ZIP extraction audit will also rerun it independently.

## 8. Documentation
- `README.md`: regenerated factual testing/selection/reproducibility claims.
- DOCX: regenerated, A4, real TOC, 26-page visual QA completed.
- PDF: regenerated from the final Word; 26 pages rendered and pixel-compared with 0 changed pages against the Word-render PDF.
- PPTX: regenerated 20-slide deck; structural overflow test PASS and full-deck montage inspected; testing/selection evidence is current.
- `DEFENSE_QA.md`, `QUALITY_AUDIT.md` and this final audit are synchronized to the same evidence.

## 9. Stale audit scan
The previous audit directory contained **45** old evidence files and was removed before creating the canonical final set. Examples of removed generations include:
- `build_metadata_arch.txt`
- `build_notebooks_arch.txt`
- `build_report.txt`
- `build_report_arch.txt`
- `build_report_arch_final.txt`
- `build_slides.txt`
- `build_slides_arch.txt`
- `compile.txt`
- `compile_arch_final.txt`
- `consistency_arch.txt`
- `consistency_arch_final.txt`
- `consistency_arch_final2.txt`
- `consistency_check.txt`
- `convert_slides_arch.txt`
- `coverage_arch.txt`
- `excel_sha.txt`
- `final_inventory.tsv`
- `final_zip_audit.txt`
- `notebook_run.txt`
- `notebook_run_arch.txt`
- `placeholder_scan.txt`
- `pytest.txt`
- `pytest_arch.txt`
- `render_docx.txt`
- `render_docx_arch.txt`
- `render_docx_arch2.txt`
- `render_docx_arch_final.txt`
- `render_pdf.txt`
- `render_pdf_arch.txt`
- `render_pdf_arch_final.txt`
- `render_slides.txt`
- `render_slides_arch.txt`
- `render_slides_arch_final.txt`
- `render_visual_qa_summary.txt`
- `secret_scan_raw.txt`
- `slides_test.txt`
- `smoke.txt`
- `smoke_arch.txt`
- `stale_reference_scan.txt`
- `streamlit_smoke.txt`
- `team_assignment_sha256_after.txt`
- `team_assignment_sha256_arch_final.txt`
- `train_arch_refactor.txt`
- `zero_byte_files.txt`
- `zero_byte_scan.txt`

Only the final canonical audit generation is intended to remain in `outputs/audit/`. A final stale-reference/path/zero-byte scan is recorded there before packaging.

## 10. Assignment Excel hash
`team/Phan_cong_cong_viec_4_thanh_vien.xlsx`:
- SHA256_BEFORE: `0b45a2030bb2e2063371bd368029f4ce09e2d818435a8ddf7deff1f5be5f1d61`
- SHA256_AFTER: `0b45a2030bb2e2063371bd368029f4ce09e2d818435a8ddf7deff1f5be5f1d61`
- Status: **PASS**

## 11. Remaining blockers
No remaining blocker has been identified for the five technical tasks in this round. Streamlit deployment is explicitly **out of scope** and is not claimed as deployed. Administrative placeholders (group/lecturer/course details) remain user-supplied submission information rather than a technical failure.

## Independent final-ZIP audit
Status: **PASS** on a clean extraction of the first packaged candidate. The extracted copy was treated as an independent checkout and rerun rather than trusting the working directory.

- Pytest in extracted ZIP: **67 passed**.
- Explicit source coverage run in extracted ZIP: **99.9%** on `src/house_price + backend` (706 statements, 1 missing).
- Extracted consistency checker: **all checks PASS**.
- Extracted canonical model SHA-256: `5101114637e8001c91f06a42737cd3cc8ee143cb1d6a3a27631a41b48f3efcf1`.
- Extracted assignment Excel SHA-256: `0b45a2030bb2e2063371bd368029f4ce09e2d818435a8ddf7deff1f5be5f1d61`.
- Extracted zero-byte scan: `NO_UNEXPECTED_ZERO_BYTE_FILES`.
- Extracted machine-specific path scan: `ABSOLUTE_PATH_SCAN_PASS`.

After recording this independent audit, the package is rebuilt once more; the rebuilt final ZIP is then extracted again for a final external verification without changing project content.
