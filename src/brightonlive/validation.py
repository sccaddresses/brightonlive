from __future__ import annotations
from datetime import datetime
from .common import postcode_valid, url_valid

PLACEHOLDER_TITLES = {"event", "events", "tbc", "untitled", "coming soon"}

def _latlon_ok(record: dict) -> bool:
    lat, lon = record.get("latitude"), record.get("longitude")
    if lat in (None, "") and lon in (None, ""):
        return True
    try:
        return -90 <= float(lat) <= 90 and -180 <= float(lon) <= 180
    except (TypeError, ValueError):
        return False

def validate_directory(record: dict) -> list[str]:
    errors = []
    if not str(record.get("name", "")).strip():
        errors.append("missing_name")
    if not str(record.get("category", "")).strip():
        errors.append("missing_category")
    if record.get("postcode") and not postcode_valid(record["postcode"]):
        errors.append("invalid_postcode")
    if record.get("website") and not url_valid(record["website"]):
        errors.append("invalid_website")
    if not _latlon_ok(record):
        errors.append("invalid_coordinates")
    if record.get("registered_office_only") and record.get("address_public"):
        errors.append("registered_office_marked_public")
    return errors

def _date_ok(value: str | None) -> bool:
    if not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False

def validate_event(record: dict) -> list[str]:
    errors = []
    title = str(record.get("title", "")).strip()
    if not title:
        errors.append("missing_title")
    elif title.lower() in PLACEHOLDER_TITLES:
        errors.append("placeholder_title")
    if not _date_ok(record.get("start")):
        errors.append("invalid_start")
    if record.get("end") and not _date_ok(record.get("end")):
        errors.append("invalid_end")
    if not record.get("venue") and not record.get("postcode") and not record.get("latitude"):
        errors.append("missing_location_signal")
    if not record.get("source_url"):
        errors.append("missing_source_url")
    elif not url_valid(record["source_url"]):
        errors.append("invalid_source_url")
    if record.get("postcode") and not postcode_valid(record["postcode"]):
        errors.append("invalid_postcode")
    if not _latlon_ok(record):
        errors.append("invalid_coordinates")
    return errors
