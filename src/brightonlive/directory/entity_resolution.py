from __future__ import annotations
from urllib.parse import urlsplit
from rapidfuzz.fuzz import ratio
from brightonlive.common import normalize_name, normalize_phone, normalize_postcode, domain_of

def keys(record: dict) -> dict[str, str]:
    return {
        "company_number": str(record.get("company_number") or "").strip().upper(),
        "domain": domain_of(record.get("website")),
        "phone": normalize_phone(record.get("phone")),
        "postcode": normalize_postcode(record.get("postcode")),
        "name": normalize_name(record.get("name")),
    }

def compatible_locations(a: dict, b: dict) -> bool:
    pa, pb = normalize_postcode(a.get("postcode")), normalize_postcode(b.get("postcode"))
    return not (pa and pb and pa != pb)

def same_entity(a: dict, b: dict) -> bool:
    ka, kb = keys(a), keys(b)
    if ka["company_number"] and ka["company_number"] == kb["company_number"]:
        return compatible_locations(a, b)
    if ka["domain"] and ka["domain"] == kb["domain"]:
        return compatible_locations(a, b)
    if ka["phone"] and ka["phone"] == kb["phone"]:
        return compatible_locations(a, b)
    if ka["postcode"] and ka["postcode"] == kb["postcode"]:
        return ratio(ka["name"], kb["name"]) >= 88
    return ratio(ka["name"], kb["name"]) >= 96 and compatible_locations(a, b)

def merge_records(a: dict, b: dict) -> dict:
    out = dict(a)
    for key, value in b.items():
        if key == "evidence":
            continue
        if out.get(key) in (None, "", [], {}):
            out[key] = value
    evidence = list(a.get("evidence", []))
    seen = {(e.get("source_key"), e.get("source_url")) for e in evidence}
    for e in b.get("evidence", []):
        marker = (e.get("source_key"), e.get("source_url"))
        if marker not in seen:
            evidence.append(e)
            seen.add(marker)
    out["evidence"] = evidence
    out["manual_verified"] = bool(a.get("manual_verified") or b.get("manual_verified"))
    out["operational_location_confirmed"] = bool(
        a.get("operational_location_confirmed") or b.get("operational_location_confirmed")
    )
    return out

def resolve(records: list[dict]) -> list[dict]:
    resolved: list[dict] = []
    for record in records:
        for idx, existing in enumerate(resolved):
            if same_entity(existing, record):
                resolved[idx] = merge_records(existing, record)
                break
        else:
            resolved.append(record)
    return resolved
