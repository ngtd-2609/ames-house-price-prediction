#!/usr/bin/env python
"""Run fresh tests + explicit source coverage and emit structured canonical evidence."""
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"outputs"/"audit"; AUDIT.mkdir(parents=True,exist_ok=True)

def run(cmd, out_path):
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    text=(p.stdout or "")+(p.stderr or "")
    Path(out_path).write_text(text if text.strip() else "COMMAND_PASS\n",encoding="utf-8")
    if p.returncode:
        raise SystemExit(f"Command failed ({p.returncode}): {' '.join(cmd)}\n{text}")
    return text

junit=AUDIT/"pytest_final.xml"
pytest_text=run([sys.executable,"-m","coverage","erase"],AUDIT/"coverage_erase.txt")
pytest_text=run([sys.executable,"-m","coverage","run","--source=src/house_price,backend","-m","pytest","-q",f"--junitxml={junit}"],AUDIT/"pytest_final.txt")
run([sys.executable,"-m","coverage","report","-m"],AUDIT/"coverage_final.txt")
raw=AUDIT/"coverage_raw.json"
run([sys.executable,"-m","coverage","json","-o",str(raw)],AUDIT/"coverage_json_build.txt")

suite=ET.parse(junit).getroot()
if suite.tag=="testsuites":
    suites=list(suite)
    tests=sum(int(s.attrib.get("tests",0)) for s in suites)
    failures=sum(int(s.attrib.get("failures",0)) for s in suites)
    errors=sum(int(s.attrib.get("errors",0)) for s in suites)
    skipped=sum(int(s.attrib.get("skipped",0)) for s in suites)
else:
    tests=int(suite.attrib.get("tests",0)); failures=int(suite.attrib.get("failures",0)); errors=int(suite.attrib.get("errors",0)); skipped=int(suite.attrib.get("skipped",0))
passed=tests-failures-errors-skipped
warnings=0
if "warnings summary" in pytest_text.lower():
    warnings=-1
summary={
    "generated_at_utc":datetime.now(timezone.utc).isoformat(),
    "tests_collected":tests,"tests_passed":passed,"tests_failed":failures+errors,"tests_skipped":skipped,
    "warnings":warnings,
    "source":"outputs/audit/pytest_final.txt",
    "structured_from":"JUnit XML generated and parsed in the same run; transient XML removed after summary creation",
}
(AUDIT/"test_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")

cov=json.loads(raw.read_text(encoding="utf-8"))
files={}
for path,item in sorted(cov["files"].items()):
    if path.startswith("src/house_price/") or path.startswith("backend/"):
        files[path]={
            "statements":item["summary"]["num_statements"],
            "missing":item["summary"]["missing_lines"],
            "coverage_pct":item["summary"]["percent_covered"],
        }
compact={
    "generated_at_utc":datetime.now(timezone.utc).isoformat(),
    "scope":["src/house_price","backend"],
    "total_statements":cov["totals"]["num_statements"],
    "total_missing":cov["totals"]["missing_lines"],
    "total_coverage":cov["totals"]["percent_covered"],
    "display_coverage":round(cov["totals"]["percent_covered"],1),
    "files":files,
}
(AUDIT/"coverage.json").write_text(json.dumps(compact,indent=2),encoding="utf-8")
raw.unlink(missing_ok=True); junit.unlink(missing_ok=True)
for transient in [AUDIT/"coverage_erase.txt",AUDIT/"coverage_json_build.txt"]:
    transient.unlink(missing_ok=True)
print(json.dumps(summary,indent=2)); print(json.dumps({k:compact[k] for k in compact if k!="files"},indent=2))
