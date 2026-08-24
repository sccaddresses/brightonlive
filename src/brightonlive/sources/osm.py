from __future__ import annotations

import time
from datetime import datetime, timezone

import requests

from .base import AdapterResult

DEFAULT_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
)


def _ordered_endpoints(configured: str) -> list[str]:
    out: list[str] = []
    for value in (configured, *DEFAULT_ENDPOINTS):
        value = str(value or "").strip().rstrip("/")
        if value and value not in out:
            out.append(value)
    return out


def _query(lat: float, lon: float, radius_km: float) -> str:
    radius = int(radius_km * 1000)
    filters = [
        '["shop"]',
        '["craft"]',
        '["office"]',
        '["healthcare"]',
        '["tourism"~"hotel|guest_house|hostel|motel|camp_site|chalet|apartment|attraction|museum|gallery"]',
        '["leisure"~"fitness_centre|sports_centre|park"]',
        '["amenity"~"restaurant|cafe|pub|bar|fast_food|pharmacy|clinic|doctors|dentist|veterinary|bank|post_office|library|community_centre|social_centre|childcare|kindergarten|fuel|car_rental|car_wash|cinema|theatre"]',
    ]
    clauses = []
    for filt in filters:
        for kind in ("node", "way", "relation"):
            clauses.append(f"{kind}{filt}(around:{radius},{lat},{lon});")
    return "[out:json][timeout:40];(" + "".join(clauses) + ");out center tags;"


def _request_payload(endpoint: str, query: str, timeout: int) -> tuple[dict, str, int]:
    failures: list[str] = []
    attempts = 0
    for endpoint_index, candidate in enumerate(_ordered_endpoints(endpoint)):
        for retry in range(2):
            attempts += 1
            try:
                response = requests.post(
                    candidate,
                    data={"data": query},
                    timeout=timeout,
                    headers={
                        "Accept": "application/json",
                        "Accept-Encoding": "gzip, deflate",
                        "User-Agent": "BrightonLive/0.2 (+https://brightonlive.uk/)",
                    },
                )
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict) or not isinstance(payload.get("elements"), list):
                    raise ValueError("Overpass response did not contain an elements array")
                return payload, candidate, attempts
            except (requests.RequestException, ValueError) as exc:
                failures.append(f"{candidate}: {type(exc).__name__}: {exc}")
                if retry == 0:
                    time.sleep(1)
        if endpoint_index < len(_ordered_endpoints(endpoint)) - 1:
            time.sleep(1)
    raise RuntimeError("All Overpass endpoints failed: " + " | ".join(failures))


def harvest(endpoint: str, lat: float, lon: float, radius_km: float, timeout: int = 45) -> AdapterResult:
    try:
        data, used_endpoint, attempts = _request_payload(endpoint, _query(lat, lon, radius_km), timeout)
    except Exception as exc:
        return AdapterResult("osm", False, [], str(exc))

    now = datetime.now(timezone.utc).isoformat()
    records = []
    for element in data.get("elements", []):
        tags = element.get("tags") or {}
        name = str(tags.get("name") or "").strip()
        if not name:
            continue
        center = element.get("center") or {}
        latv = element.get("lat", center.get("lat"))
        lonv = element.get("lon", center.get("lon"))
        category = (
            tags.get("amenity")
            or tags.get("shop")
            or tags.get("tourism")
            or tags.get("leisure")
            or tags.get("office")
            or tags.get("craft")
            or tags.get("healthcare")
            or "place"
        )
        osm_id = f"{element.get('type')}/{element.get('id')}"
        source_url = f"https://www.openstreetmap.org/{osm_id}"
        address = " ".join(
            filter(None, [tags.get("addr:housenumber"), tags.get("addr:housename"), tags.get("addr:street")])
        )
        records.append(
            {
                "name": name,
                "category": category,
                "address": address,
                "postcode": tags.get("addr:postcode", ""),
                "latitude": latv,
                "longitude": lonv,
                "website": tags.get("website") or tags.get("contact:website") or "",
                "phone": tags.get("phone") or tags.get("contact:phone") or "",
                "email": tags.get("email") or tags.get("contact:email") or "",
                "address_public": True,
                "phone_public": True,
                "email_public": True,
                "manual_verified": False,
                "operational_location_confirmed": False,
                "osm_id": osm_id,
                "evidence": [
                    {
                        "source_key": "osm",
                        "source_url": source_url,
                        "source_owner": "OpenStreetMap contributors",
                        "source_type": "community_open_data",
                        "retrieved_at": now,
                        "fields": ["name", "category", "address", "postcode", "geo", "website", "phone", "email"],
                    }
                ],
            }
        )
    return AdapterResult(
        "osm",
        True,
        records,
        f"{len(records)} OSM candidates via {used_endpoint} after {attempts} attempt(s)",
        {"endpoint": used_endpoint, "attempts": attempts},
    )
