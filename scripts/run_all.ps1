$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "src;."
python scripts/audit_data.py
python scripts/train_full_project.py
python scripts/build_metadata.py
python scripts/build_notebooks.py
python scripts/execute_notebooks.py
coverage run -m pytest -q
coverage report -m
python scripts/smoke_test.py
python -m compileall -q src backend app scripts tests
Write-Host "ALL_CHECKS_FINISHED"
