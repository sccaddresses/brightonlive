from __future__ import annotations
from pathlib import Path
from brightonlive.integrity import attach_integrity
from brightonlive.validation import validate_directory
from brightonlive.verification import directory_decision
from brightonlive.privacy import public_directory_record
from .entity_resolution import resolve
from .exporters import export_directory

def process_directory(candidates: list[dict], cfg: dict, out_dir: str | Path) -> dict:
    policy = cfg["policy"]
    records = []
    for record in resolve(candidates):
        record = dict(record)
        record["validation_errors"] = validate_directory(record)
        decision, reasons = directory_decision(record, policy)
        record["verification_status"] = decision
        record["verification_reasons"] = reasons
        records.append(attach_integrity(record))

    public = [public_directory_record(r) for r in records if r["verification_status"] == "publication_ready"]
    review = [r for r in records if r["verification_status"] != "publication_ready"]
    return export_directory(records, public, review, out_dir, cfg)
