"""Tao metadata/manifest tu canonical outputs/summary.json."""
from __future__ import annotations
import hashlib, json, platform
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
summary=json.loads((ROOT/'outputs'/'summary.json').read_text(encoding='utf-8'))
def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
model=ROOT/'models'/'house_price_pipeline.joblib'
metadata={
    'model_name':'Ames House Price Regressor','artifact_version':'2.0.0','task':'supervised regression','target':'SalePrice',
    'selected_model':summary['selected_model'],'selected_params':summary['selected_params'],'validation_metrics':summary['validation_metrics'],'test_metrics':summary['test_metrics'],
    'test_bootstrap_ci':summary['test_bootstrap_ci'],'cv_stability':summary['selected_model_cv_stability'],'training_rows':1314,'test_rows':146,
    'raw_feature_count':summary['dataset']['input_features_raw'],'engineered_feature_count':summary['dataset']['engineered_feature_count'],'random_state':42,
    'end_to_end_raw_input':True,'contains_feature_engineering':True,'model_sha256':sha256(model),'schema_sha256':sha256(ROOT/'models'/'input_schema.json'),
    'created_at_utc':summary['generated_at_utc'],'runtime_environment':summary['environment'],
    'limitations':['Du lieu Ames lich su, khong dai dien truc tiep cho thi truong Viet Nam.','Sai so tuyet doi tang o mot so nhom nha gia cao.','Khong co bien vi mo, lai suat, toa do khoang cach hay tinh trang phap ly.']}
(ROOT/'models'/'model_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
manifest_paths=[ROOT/'data'/'house_train_80.csv',ROOT/'data'/'house_validation_10.csv',ROOT/'data'/'house_test_10.csv',model,ROOT/'models'/'input_schema.json',ROOT/'outputs'/'summary.json',ROOT/'models'/'model_metadata.json']
manifest={'generated_at_utc':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha256(p)} for p in manifest_paths]}
(ROOT/'outputs'/'run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('METADATA_AND_MANIFEST_CREATED')
