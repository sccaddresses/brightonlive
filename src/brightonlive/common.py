from __future__ import annotations
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

POSTCODE_RE = re.compile(r"^([A-Z]{1,2}\d[A-Z\d]?)\s*(\d[A-Z]{2})$", re.I)

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def normalize_space(value: str | None) -> str:
    return " ".join((value or "").split()).strip()

def normalize_name(value: str | None) -> str:
    value = normalize_space(value).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return normalize_space(value)

def normalize_postcode(value: str | None) -> str:
    v = re.sub(r"\s+", "", (value or "").upper())
    if len(v) < 5:
        return v
    return f"{v[:-3]} {v[-3:]}"

def postcode_valid(value: str | None) -> bool:
    return bool(POSTCODE_RE.match(normalize_postcode(value)))

def normalize_phone(value: str | None) -> str:
    digits = re.sub(r"\D+", "", value or "")
    if digits.startswith("44"):
        digits = "0" + digits[2:]
    return digits

def domain_of(url: str | None) -> str:
    if not url:
        return ""
    try:
        host = urlsplit(url).hostname or ""
    except ValueError:
        return ""
    host = host.lower()
    return host[4:] if host.startswith("www.") else host

def url_valid(url: str | None) -> bool:
    if not url:
        return False
    try:
        p = urlsplit(url)
    except ValueError:
        return False
    return p.scheme in {"http", "https"} and bool(p.netloc)

def parse_bool(value, default=False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}
