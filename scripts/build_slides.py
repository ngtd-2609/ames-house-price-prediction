#!/usr/bin/env python
"""Build the final PowerPoint deck using pptxgenjs."""
from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
res = subprocess.run(['node', 'scripts/build_slides.js'], cwd=ROOT, text=True, capture_output=True)
if res.returncode != 0:
    print(res.stdout)
    print(res.stderr, file=sys.stderr)
    raise SystemExit(res.returncode)
out = ROOT/'slides'/'Slide_Du_bao_gia_nha_Hoan_chinh.pptx'
if not out.exists() or out.stat().st_size == 0:
    raise FileNotFoundError(out)
print('SLIDES_BUILT', out, out.stat().st_size)
