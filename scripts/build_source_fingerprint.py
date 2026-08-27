#!/usr/bin/env python
"""Generate a machine-readable fingerprint used by notebooks for freshness checks."""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKED = [
    "scripts/train_full_project.py",
    "src/house_price/selection.py",
    "src/house_price/tuning.py",
    "src/house_price/reporting.py",
    "src/house_price/validation.py",
]


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


payload = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "files": {rel: digest(ROOT / rel) for rel in TRACKED},
}
(ROOT / "outputs" / "source_fingerprint.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("SOURCE_FINGERPRINT_BUILT", len(TRACKED), "files")
