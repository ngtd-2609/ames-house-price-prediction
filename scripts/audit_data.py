"""CLI kiem tra data integrity va checksum ma khong huan luyen model."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from house_price.data import load_house_data, sha256_file
from house_price.validation import validate_splits

frames={k:load_house_data(v) for k,v in {"train":"house_train_80.csv","validation":"house_validation_10.csv","test":"house_test_10.csv"}.items()}
result=validate_splits(frames['train'],frames['validation'],frames['test'])
result['hashes']={name:sha256_file(ROOT/'data'/filename) for name,filename in {"train":"house_train_80.csv","validation":"house_validation_10.csv","test":"house_test_10.csv"}.items()}
print(json.dumps(result,ensure_ascii=False,indent=2,default=str)); print('DATA_AUDIT_PASS')
