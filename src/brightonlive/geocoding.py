from __future__ import annotations

from urllib.parse import quote
from datetime import datetime, timezone

import requests

from .common import normalize_postcode


def geocode_postcode(postcode: str, timeout: int = 10) -> dict | None:
    clean = normalize_postcode(postcode)
    if not clean:
        return None
    response = requests.get(
        f"https://api.postcodes.io/postcodes/{quote(clean)}",
        timeout=timeout,
        headers={"User-Agent": "BrightonLive/0.2 postcode-geocoder"},
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    payload = response.json()
    result = payload.get("result") or {}
    if result.get("latitude") is None or result.get("longitude") is None:
        return None
    return {
        "postcode": normalize_postcode(result.get("postcode") or clean),
        "latitude": float(result["latitude"]),
        "longitude": float(result["longitude"]),
        "source": "postcodes.io",
    }


def enrich_records(records: list[dict], timeout: int = 10) -> list[dict]:
    cache: dict[str, dict | None] = {}
    out: list[dict] = []
    for record in records:
        row = dict(record)
        if row.get("latitude") not in (None, "") and row.get("longitude") not in (None, ""):
            out.append(row)
            continue
        postcode = normalize_postcode(row.get("postcode"))
        if not postcode:
            out.append(row)
            continue
        if postcode not in cache:
            try:
                cache[postcode] = geocode_postcode(postcode, timeout=timeout)
            except requests.RequestException:
                cache[postcode] = None
        geo = cache[postcode]
        if geo:
            row["postcode"] = geo["postcode"]
            row["latitude"] = geo["latitude"]
            row["longitude"] = geo["longitude"]
            evidence = list(row.get("evidence") or [])
            evidence.append({
                "source_key": "postcodes_io",
                "source_url": f"https://api.postcodes.io/postcodes/{quote(postcode)}",
                "source_owner": "postcodes.io",
                "source_type": "public_geocoder",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "fields": ["postcode", "geo"],
            })
            row["evidence"] = evidence
        out.append(row)
    return out
