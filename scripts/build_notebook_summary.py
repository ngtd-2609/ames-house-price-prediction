#!/usr/bin/env python
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
import nbformat

ROOT=Path(__file__).resolve().parents[1]
rows={}
for key,name in [("detailed","House_Price_Prediction_Detailed.ipynb"),("basic","House_Price_Prediction_Basic.ipynb")]:
    path=ROOT/"notebooks"/name
    nb=nbformat.read(path,as_version=4)
    errors=[o for c in nb.cells if c.cell_type=="code" for o in c.get("outputs",[]) if o.get("output_type")=="error"]
    executed_codes=[c for c in nb.cells if c.cell_type=="code"]
    missing_exec=[c for c in executed_codes if c.get("execution_count") is None]
    rows[f"{key}_notebook"]=name
    rows[f"{key}_cells"]=len(nb.cells)
    rows[f"{key}_code_cells"]=len(executed_codes)
    rows[f"{key}_status"]="PASS" if not errors and not missing_exec else "FAIL"
    rows[f"{key}_execution_errors"]=len(errors)
rows["generated_at_utc"]=datetime.now(timezone.utc).isoformat()
rows["executed_with"]="scripts/execute_notebooks.py"
(ROOT/"outputs"/"notebook_summary.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(rows,indent=2))
