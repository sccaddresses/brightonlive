from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

VOLATILE_KEYS = {"integrity_sha256", "updated_at", "run_id"}

def canonical_payload(record: dict[str, Any]) -> bytes:
    stable = {k: v for k, v in record.items() if k not in VOLATILE_KEYS}
    return json.dumps(stable, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

def record_sha256(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_payload(record)).hexdigest()

def file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def attach_integrity(record: dict[str, Any]) -> dict[str, Any]:
    record = dict(record)
    record["integrity_sha256"] = record_sha256(record)
    return record
