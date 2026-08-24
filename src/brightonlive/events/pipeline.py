from __future__ import annotations
from pathlib import Path
from brightonlive.integrity import attach_integrity
from brightonlive.validation import validate_event
from brightonlive.verification import event_decision
from .normalization import normalise_event
from .dedupe import dedupe
from .exporters import export_events

def process_events(candidates: list[dict], cfg: dict, out_dir: str | Path) -> dict:
    policy = cfg["policy"]
    records = []
    for record in dedupe([normalise_event(r) for r in candidates]):
        record["validation_errors"] = validate_event(record)
        decision, reasons = event_decision(record, policy)
        record["verification_status"] = decision
        record["verification_reasons"] = reasons
        records.append(attach_integrity(record))

    public = [r for r in records if r["verification_status"] == "publication_ready"]
    review = [r for r in records if r["verification_status"] != "publication_ready"]
    return export_events(records, public, review, out_dir, cfg)
