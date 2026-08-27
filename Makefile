.PHONY: setup audit train metadata notebooks test smoke app compile final-audit

setup:
	python -m venv .venv
	. .venv/bin/activate && python -m pip install --upgrade pip && python -m pip install -r requirements.txt && python -m pip install -e .

audit:
	PYTHONPATH=src python scripts/audit_data.py

train:
	PYTHONPATH=src python scripts/train_full_project.py

metadata:
	PYTHONPATH=src python scripts/build_metadata.py

notebooks:
	PYTHONPATH=src python scripts/build_notebooks.py
	PYTHONPATH=src:. python scripts/execute_notebooks.py

test:
	PYTHONPATH=src:. coverage run -m pytest -q
	PYTHONPATH=src:. coverage report -m

smoke:
	PYTHONPATH=src:. python scripts/smoke_test.py

compile:
	python -m compileall -q src backend app scripts tests

app:
	PYTHONPATH=src:. streamlit run app/Home.py

final-audit: audit train metadata notebooks test smoke compile
