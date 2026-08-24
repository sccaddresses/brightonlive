from __future__ import annotations
from pathlib import Path

from brightonlive.config import load_yaml
from brightonlive.integrity import attach_integrity
from brightonlive.locality import in_public_scope
from brightonlive.taxonomy import normalise_category
from brightonlive.validation import validate_event
from brightonlive.verification import event_decision
from .normalization import normalise_event
from .dedupe import dedupe
from .exporters import export_events


def process_events(candidates: list[dict], cfg: dict, out_dir: str | Path) -> dict:
    policy = cfg["policy"]
    taxonomy = load_yaml(cfg["events"]["taxonomy"])
    category_items = taxonomy.get("event_categories", [])
    records = []
    normalised = []
    for candidate in candidates:
        row = normalise_event(candidate)
        row["category"] = normalise_category(row.get("category", ""), category_items, fallback="Other")
        normalised.append(row)

    for record in dedupe(normalised):
        record["public_scope"] = in_public_scope(record, cfg["location"])
        record["validation_errors"] = validate_event(record)
        if not record["public_scope"]:
            record["validation_errors"].append("outside_public_scope")
        decision, reasons = event_decision(record, policy)
        record["verification_status"] = decision
        record["verification_reasons"] = reasons
        records.append(attach_integrity(record))

    public = [r for r in records if r["verification_status"] == "publication_ready"]
    review = [r for r in records if r["verification_status"] != "publication_ready"]
    return export_events(records, public, review, out_dir, cfg)
