from __future__ import annotations
from .provenance import evidence_domains, provenance_complete

CLASS_A = {"authoritative_class_a", "public_authority"}
OWNED = {"owned_primary", "first_party", "first_party_ticketing", "official_destination"}

def directory_decision(record: dict, policy: dict) -> tuple[str, list[str]]:
    reasons = []
    errors = record.get("validation_errors") or []
    if errors:
        return "held_for_review", [f"validation:{e}" for e in errors]
    if not provenance_complete(record):
        return "held_for_review", ["provenance_incomplete"]
    if record.get("registered_office_only") and not record.get("operational_location_confirmed"):
        return "held_for_review", ["registered_office_not_operational_evidence"]

    if record.get("manual_verified"):
        return "publication_ready", ["manual_verified"]

    evidence = record.get("evidence") or []
    source_types = {e.get("source_type") for e in evidence}
    if policy.get("allow_class_a_single_source", True) and source_types.intersection(CLASS_A):
        return "publication_ready", ["authoritative_class_a"]

    if policy.get("allow_owned_source_single_source", True) and source_types.intersection(OWNED):
        return "publication_ready", ["organisation_owned_primary"]

    independent = evidence_domains(evidence)
    need = int(policy.get("minimum_independent_sources", 2))
    if len(independent) >= need:
        return "publication_ready", [f"{len(independent)}_independent_sources"]

    reasons.append("insufficient_corroboration")
    return "verification_pending", reasons

def event_decision(record: dict, policy: dict) -> tuple[str, list[str]]:
    errors = record.get("validation_errors") or []
    if errors:
        return "held_for_review", [f"validation:{e}" for e in errors]
    if not provenance_complete(record):
        return "held_for_review", ["provenance_incomplete"]
    if record.get("manual_verified"):
        return "publication_ready", ["manual_verified"]
    evidence = record.get("evidence") or []
    source_types = {e.get("source_type") for e in evidence}
    if source_types.intersection(OWNED | CLASS_A):
        return "publication_ready", ["primary_or_official_source"]
    if len(evidence_domains(evidence)) >= int(policy.get("minimum_independent_sources", 2)):
        return "publication_ready", ["corroborated"]
    return "verification_pending", ["primary_source_not_confirmed"]
