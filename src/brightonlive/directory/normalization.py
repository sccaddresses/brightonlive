from __future__ import annotations

from brightonlive.config import load_yaml
from brightonlive.taxonomy import normalise_category
from brightonlive.common import normalize_space


def normalise_directory_record(record: dict, taxonomy_path: str) -> dict:
    out = dict(record)
    taxonomy = load_yaml(taxonomy_path)
    items = taxonomy.get("directory_categories", [])
    raw_category = normalize_space(out.get("category"))
    out["source_category"] = raw_category
    out["category"] = normalise_category(raw_category, items, fallback="Other")
    out["name"] = normalize_space(out.get("name"))
    out["address"] = normalize_space(out.get("address"))
    return out


def fhrs_consumer_eligible(record: dict, policy: dict) -> tuple[bool, str]:
    """Separate authoritative FHRS evidence from consumer-directory suitability."""
    evidence = record.get("evidence") or []
    if not any(e.get("source_key") == "fhrs" for e in evidence):
        return True, "not_fhrs"

    raw = str(record.get("source_category") or record.get("category") or "").casefold()
    allow = [str(x).casefold() for x in policy.get("fhrs_consumer_allow_markers", [])]
    hold = [str(x).casefold() for x in policy.get("fhrs_consumer_hold_markers", [])]
    if any(marker and marker in raw for marker in hold):
        return False, "fhrs_non_consumer_type"
    if allow and not any(marker and marker in raw for marker in allow):
        return False, "fhrs_type_not_allowlisted"
    return True, "fhrs_consumer_type"
