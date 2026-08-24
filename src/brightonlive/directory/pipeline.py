from __future__ import annotations
from pathlib import Path

from brightonlive.integrity import attach_integrity
from brightonlive.locality import in_public_scope
from brightonlive.validation import validate_directory
from brightonlive.verification import directory_decision
from brightonlive.privacy import public_directory_record
from .entity_resolution import resolve
from .exporters import export_directory
from .normalization import normalise_directory_record, fhrs_consumer_eligible


def process_directory(candidates: list[dict], cfg: dict, out_dir: str | Path) -> dict:
    policy = cfg["policy"]
    taxonomy_path = cfg["directory"]["taxonomy"]
    consumer_policy = cfg.get("directory_publication", {})
    location = cfg["location"]
    normalised = [normalise_directory_record(r, taxonomy_path) for r in candidates]
    records = []
    for record in resolve(normalised):
        record = dict(record)
        record["public_scope"] = in_public_scope(record, location)
        consumer_ok, consumer_reason = fhrs_consumer_eligible(record, consumer_policy)
        record["consumer_directory_eligible"] = consumer_ok
        record["consumer_directory_reason"] = consumer_reason
        record["validation_errors"] = validate_directory(record)
        if not record["public_scope"]:
            record["validation_errors"].append("outside_public_scope")
        if not consumer_ok:
            record["validation_errors"].append(consumer_reason)
        decision, reasons = directory_decision(record, policy)
        record["verification_status"] = decision
        record["verification_reasons"] = reasons
        records.append(attach_integrity(record))

    public = [public_directory_record(r) for r in records if r["verification_status"] == "publication_ready"]
    review = [r for r in records if r["verification_status"] != "publication_ready"]
    return export_directory(records, public, review, out_dir, cfg)
