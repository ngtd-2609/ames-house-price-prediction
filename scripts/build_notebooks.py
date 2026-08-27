"""Build Detailed and Basic notebooks with an explicit model-lock/test-unlock protocol."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / "notebooks"
NB_DIR.mkdir(exist_ok=True)


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


setup = '''from pathlib import Path
import hashlib, json, sys, pandas as pd, numpy as np
ROOT = Path.cwd() if (Path.cwd()/"data").exists() else Path.cwd().parent
if str(ROOT/"src") not in sys.path: sys.path.insert(0, str(ROOT/"src"))
from house_price.data import load_house_data, split_xy, sha256_file
print("PROJECT_ROOT: <project root detected>")'''

freshness = '''summary_path = ROOT/"outputs"/"summary.json"
policy_path = ROOT/"outputs"/"model_selection_policy.json"
fingerprint_path = ROOT/"outputs"/"source_fingerprint.json"
summary = json.loads(summary_path.read_text(encoding="utf-8"))
policy = json.loads(policy_path.read_text(encoding="utf-8"))
fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))
issues = []
# Data freshness uses file checksums only; test target values are not loaded here.
for item in summary.get("data_hashes", []):
    path = ROOT/item["file"]
    if sha256_file(path) != item["sha256"]: issues.append(f"data hash mismatch: {item['file']}")
model_path = ROOT/summary["artifact"]["path"]
if sha256_file(model_path) != summary["artifact"]["model_sha256"]: issues.append("artifact hash mismatch")
if summary["selected_model"] != policy["locked_model"]: issues.append("selected model mismatch")
if summary["selected_params"] != policy["locked_params"]: issues.append("selected params mismatch")
for rel, expected in fingerprint.get("files", {}).items():
    if sha256_file(ROOT/rel) != expected: issues.append(f"source fingerprint mismatch: {rel}")
if not summary.get("generated_at_utc") or not fingerprint.get("generated_at_utc"): issues.append("missing generated_at timestamp")
if issues:
    raise RuntimeError("STALE EVIDENCE: " + "; ".join(issues) + ". Regenerate canonical evidence before using this notebook.")
print("FRESHNESS: PASS")
print("summary generated_at:", summary["generated_at_utc"])
print("fingerprint generated_at:", fingerprint["generated_at_utc"])'''


detailed = nbf.v4.new_notebook(cells=[
    md("# Dự báo giá nhà Ames/Kaggle — Notebook Detailed\n\nNotebook trình bày protocol thực nghiệm theo ba pha: Development → MODEL LOCK → Test. Logic ML canonical nằm trong `src/house_price`."),
    md("## 1. Protocol chống leakage\n**Phase A — Development:** chỉ dùng train + validation cho audit, EDA, benchmark, tuning và selection. **Phase B — Lock:** đọc policy/model/params đã khóa. **Phase C — Test:** sau `MODEL LOCKED` mới load và tách `y_test`."),
    code(setup),
    md("## Phase A — Development (train + validation only)"),
    code('''train = load_house_data("house_train_80.csv")
validation = load_house_data("house_validation_10.csv")
assert train.shape == (1168, 81) and validation.shape == (146, 81)
assert list(train.columns) == list(validation.columns)
X_train, y_train = split_xy(train); X_val, y_val = split_xy(validation)
assert "SalePrice" not in X_train and "Id" not in X_train
print("Development shapes:", X_train.shape, X_val.shape)'''),
    md("### 2. Freshness gate trước khi đọc kết quả canonical"),
    code(freshness),
    md("### 3. Feature engineering và preprocessing contract"),
    code('''from house_price.config import ENGINEERED_FEATURES
from house_price.features import engineer_features
engineered = engineer_features(X_train.head(3))
print("Added features:", ENGINEERED_FEATURES)
print("Raw → engineered:", X_train.shape[1], "→", engineered.shape[1])'''),
    md("### 4. EDA train/validation"),
    code('''from IPython.display import Image, display
display(Image(filename=str(ROOT/"outputs/figures/01_target_distribution.png")))
display(Image(filename=str(ROOT/"outputs/figures/02_missingness_top20.png")))
display(Image(filename=str(ROOT/"outputs/figures/06_split_distribution_check.png")))
pd.read_csv(ROOT/"outputs/tables/split_drift_numeric.csv")'''),
    md("### 5. Benchmark và tuning — không có test"),
    code('''benchmark = pd.read_csv(ROOT/"outputs/tables/validation_model_comparison.csv")
benchmark.round(4)'''),
    code('''tuning_table = pd.read_csv(ROOT/"outputs/tables/tuning_results.csv")
tuning_table.round(4)'''),
    md("## Phase B — MODEL LOCK"),
    code('''from house_price.selection import ModelSelectionPolicy
print("model_selection_policy:", policy)
print("selected_model:", summary["selected_model"])
print("selected_params:", summary["selected_params"])
print("selection_reason: validation RMSE with documented Ridge tolerance/CV tie-break; test unavailable")
assert policy["uses_test"] is False
assert policy["locked_model"] == summary["selected_model"]
assert policy["locked_params"] == summary["selected_params"]
print("MODEL LOCKED")'''),
    md("## Phase C — Test unlock và final evaluation"),
    code('''test = load_house_data("house_test_10.csv")
from house_price.validation import validate_splits
print(validate_splits(train, validation, test))
X_test, y_test = split_xy(test)
print("TEST UNLOCKED AFTER MODEL LOCK:", X_test.shape)'''),
    code('''pd.DataFrame([summary["test_metrics"]])'''),
    code('''summary["test_bootstrap_ci"]'''),
    code('''display(Image(filename=str(ROOT/"outputs/figures/08_actual_vs_predicted.png")))
display(Image(filename=str(ROOT/"outputs/figures/09_residual_vs_predicted.png")))
display(Image(filename=str(ROOT/"outputs/figures/10_residual_distribution.png")))'''),
    md("## 6. Error analysis và explainability"),
    code('''display(Image(filename=str(ROOT/"outputs/figures/11_error_by_price_quartile.png")))
pd.read_csv(ROOT/"outputs/tables/error_by_price_quartile.csv")'''),
    code('''display(Image(filename=str(ROOT/"outputs/figures/12_permutation_importance.png")))
pd.read_csv(ROOT/"outputs/tables/permutation_importance.csv").head(15)'''),
    md("## 7. Artifact end-to-end regression check"),
    code('''import joblib
model = joblib.load(ROOT/"models/house_price_pipeline.joblib")
print(model.regressor.named_steps.keys())
p = model.predict(X_test.head(3)); print(p)
assert np.allclose(p, summary["artifact"]["reload_predictions"], rtol=0, atol=1e-6)'''),
    md("## 8. Kết luận\nModel được chọn và khóa chỉ từ train/validation. Test target chỉ được load sau cell `MODEL LOCKED`; artifact cuối nhận raw 79 features và giữ nguyên model canonical ElasticNet."),
])

basic = nbf.v4.new_notebook(cells=[
    md("# Dự báo giá nhà — Notebook Basic\n\nBản ngắn vẫn giữ đúng Development → MODEL LOCK → Test."),
    code(setup),
    md("## Phase A — Development"),
    code('''tr = load_house_data("house_train_80.csv"); va = load_house_data("house_validation_10.csv")
Xtr, ytr = split_xy(tr); Xva, yva = split_xy(va)
assert tr.shape == (1168, 81) and va.shape == (146, 81)
print("Development only:", Xtr.shape, Xva.shape)'''),
    code(freshness),
    md("## Phase B — MODEL LOCK"),
    code('''print("Locked model:", summary["selected_model"])
print("Locked params:", summary["selected_params"])
assert policy["locked_model"] == summary["selected_model"]
assert policy["locked_params"] == summary["selected_params"]
assert policy["uses_test"] is False
print("MODEL LOCKED")'''),
    md("## Phase C — Test"),
    code('''te = load_house_data("house_test_10.csv")
from house_price.validation import validate_splits
print(validate_splits(tr, va, te))
Xte, yte = split_xy(te)
print("TEST UNLOCKED AFTER MODEL LOCK:", Xte.shape)'''),
    code('''from house_price.modeling import build_end_to_end_estimator, model_definitions
from house_price.evaluation import regression_metrics
base = model_definitions()[summary["selected_model"]]
model = build_end_to_end_estimator(Xtr, base)
model.set_params(**summary["selected_params"])
model.fit(pd.concat([Xtr, Xva], ignore_index=True), pd.concat([ytr, yva], ignore_index=True))
pred = model.predict(Xte)
metrics = regression_metrics(yte, pred)
metrics'''),
    code('''for key, value in summary["test_metrics"].items():
    assert abs(metrics[key] - value) < 1e-6
print("PASS: Basic reproduces canonical metrics")'''),
    code('''import joblib, tempfile
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp)/"basic_model.joblib"
    joblib.dump(model, path); loaded = joblib.load(path)
    assert np.allclose(loaded.predict(Xte.head(3)), pred[:3])
print("PASS: temporary serialization only; canonical artifact unchanged")'''),
    md("## Kết luận\nBasic notebook không mở `y_test` trước model lock và tái tạo đúng canonical metrics."),
])

for nb in (detailed, basic):
    nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata.language_info = {"name": "python"}

nbf.write(detailed, NB_DIR / "House_Price_Prediction_Detailed.ipynb")
nbf.write(basic, NB_DIR / "House_Price_Prediction_Basic.ipynb")
print("NOTEBOOKS_BUILT", len(detailed.cells), len(basic.cells))
