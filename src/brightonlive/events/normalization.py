from __future__ import annotations
from datetime import datetime
from dateutil import parser as date_parser
from brightonlive.common import normalize_space

def iso_datetime(value: str | None) -> str:
    if not value:
        return ""
    try:
        return date_parser.parse(value).isoformat()
    except (ValueError, TypeError, OverflowError):
        return str(value).strip()

def normalise_event(record: dict) -> dict:
    out = dict(record)
    out["title"] = normalize_space(out.get("title"))
    out["venue"] = normalize_space(out.get("venue"))
    out["start"] = iso_datetime(out.get("start"))
    out["end"] = iso_datetime(out.get("end"))
    return out
