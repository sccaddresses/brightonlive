from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from urllib.parse import quote

import requests

from .common import normalize_postcode


def postcode_prefix(value: str | None) -> str:
    postcode = normalize_postcode(value)
    return postcode.split(" ", 1)[0] if postcode else ""


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance; deterministic and dependency free."""
    r = 6371.0088
    p1, p2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dlambda / 2) ** 2
    return 2 * r * asin(sqrt(a))


def in_public_scope(record: dict, location: dict) -> bool:
    """Return whether a record belongs on the consumer-facing locality site.

    Prefer configured postcode districts when the record has a postcode.  If a source
    lacks a postcode, fall back to a deliberately tighter public radius than the broad
    discovery radius.  This lets harvesting remain generous without leaking neighbouring
    towns into the public Brighton guide.
    """
    prefixes = tuple(str(x).upper() for x in location.get("core_postcode_prefixes", []))
    prefix = postcode_prefix(record.get("postcode"))
    if prefix:
        return any(prefix == allowed or prefix.startswith(allowed) for allowed in prefixes)

    try:
        lat = float(record.get("latitude"))
        lon = float(record.get("longitude"))
        centre_lat = float(location["latitude"])
        centre_lon = float(location["longitude"])
    except (TypeError, ValueError, KeyError):
        return False
    radius = float(location.get("public_radius_km", location.get("radius_km", 10.0)))
    return distance_km(lat, lon, centre_lat, centre_lon) <= radius


def lookup_uk_postcode(postcode: str, timeout: int = 15) -> dict:
    """Resolve a UK postcode using the public postcodes.io service.

    This is the seed for the future postcode-driven 'one engine, any locality' mode.
    Nothing in the Brighton production run depends on it unless explicitly invoked.
    """
    clean = normalize_postcode(postcode)
    response = requests.get(
        f"https://api.postcodes.io/postcodes/{quote(clean)}",
        timeout=timeout,
        headers={"User-Agent": "BrightonLive/0.2 postcode-locality"},
    )
    response.raise_for_status()
    payload = response.json()
    result = payload.get("result") or {}
    if not result:
        raise ValueError(f"Postcode not found: {clean}")
    return {
        "postcode": clean,
        "latitude": float(result["latitude"]),
        "longitude": float(result["longitude"]),
        "admin_district": result.get("admin_district") or "",
        "parliamentary_constituency": result.get("parliamentary_constituency") or "",
        "country": result.get("country") or "",
    }
