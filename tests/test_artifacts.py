import hashlib,json
import joblib
from house_price.artifacts import build_input_schema,load_model
from house_price.config import MODEL_DIR
from house_price.data import load_house_data

def sha(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def test_schema_has_79_fields_and_numeric_domains():
    tr=load_house_data('house_train_80.csv'); s=build_input_schema(tr); assert s['feature_count']==79; q=next(f for f in s['fields'] if f['name']=='OverallQual'); assert q['min']<=q['default']<=q['max']; assert q['label']

def test_saved_artifact_is_end_to_end_and_metadata_hash_matches():
    model=load_model(); steps=model.regressor.named_steps; assert 'feature_engineering' in steps and 'preprocessor' in steps and 'model' in steps
    meta=json.loads((MODEL_DIR/'model_metadata.json').read_text(encoding='utf-8')); assert meta['contains_feature_engineering'] is True; assert meta['model_sha256']==sha(MODEL_DIR/'house_price_pipeline.joblib')

def test_joblib_reload_is_consistent():
    a=load_model(); b=joblib.load(MODEL_DIR/'house_price_pipeline.joblib'); tr=load_house_data('house_test_10.csv').drop(columns=['Id','SalePrice']).head(2); assert (a.predict(tr)==b.predict(tr)).all()
