from __future__ import annotations
import hashlib
from brightonlive.common import normalize_name, normalize_postcode

def fingerprint(record: dict) -> str:
    start = str(record.get("start") or "")[:10]
    basis = "|".join([
        normalize_name(record.get("title")),
        start,
        normalize_name(record.get("venue")),
        normalize_postcode(record.get("postcode")),
    ])
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()

def dedupe(records: list[dict]) -> list[dict]:
    out, seen = [], {}
    for record in records:
        fp = fingerprint(record)
        if fp not in seen:
            record = dict(record)
            record["event_fingerprint"] = fp
            seen[fp] = len(out)
            out.append(record)
        else:
            idx = seen[fp]
            existing = out[idx]
            evidence = existing.setdefault("evidence", [])
            markers = {(e.get("source_key"), e.get("source_url")) for e in evidence}
            for e in record.get("evidence", []):
                marker = (e.get("source_key"), e.get("source_url"))
                if marker not in markers:
                    evidence.append(e)
                    markers.add(marker)
            existing["manual_verified"] = bool(existing.get("manual_verified") or record.get("manual_verified"))
    return out
