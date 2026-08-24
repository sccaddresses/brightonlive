from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json, os

from .config import load_project, load_yaml
from .sources import manual, jsonld, osm, fhrs, companies_house, structured_pages
from .directory.pipeline import process_directory
from .events.pipeline import process_events
from .website.builder import install_public_feeds
from .geocoding import enrich_records as geocode_records


def _write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _event_sources(registry: dict) -> list[dict]:
    out = []
    for source in registry.get("suppliers", []):
        if not source.get("enabled", False):
            continue
        urls = source.get("urls") or {}
        url = urls.get("events") or urls.get("programme") or urls.get("website")
        if not url:
            continue
        categories = source.get("categories") or []
        out.append(
            {
                "key": source["key"],
                "name": source["name"],
                "url": url,
                "source_type": source.get("source_class", "first_party"),
                "default_venue": source.get("default_venue") or source.get("venue") or source.get("name", ""),
                "default_postcode": source.get("default_postcode") or source.get("postcode") or "",
                "default_category": categories[0] if categories else "Uncategorised",
                "latitude": source.get("latitude"),
                "longitude": source.get("longitude"),
            }
        )
    return out


def run(config_path="config/brighton.yaml", offline=False, fixtures=False) -> dict:
    cfg = load_project(config_path)
    out_dir = Path(cfg["outputs"]["directory"])
    out_dir.mkdir(parents=True, exist_ok=True)
    source_health = []

    # Directory candidates
    directory_candidates = []
    directory_file = cfg["directory"]["fixture_csv"] if fixtures else cfg["directory"]["manual_csv"]
    res = manual.directory(directory_file)
    directory_candidates.extend(res.records)
    source_health.append(res.__dict__)

    if not offline:
        registry = load_yaml(cfg["directory"]["source_registry"])
        by_key = {s["key"]: s for s in registry.get("sources", []) if s.get("enabled")}
        loc = cfg["location"]

        if "fhrs" in by_key:
            source = by_key["fhrs"]
            res = fhrs.harvest(source["endpoint"], loc["latitude"], loc["longitude"], loc["radius_miles"])
            directory_candidates.extend(res.records)
            source_health.append(res.__dict__)

        if "osm" in by_key:
            source = by_key["osm"]
            res = osm.harvest(source["endpoint"], loc["latitude"], loc["longitude"], loc["radius_km"])
            directory_candidates.extend(res.records)
            source_health.append(res.__dict__)

        if "companies_house" in by_key:
            res = companies_house.discover(os.getenv("COMPANIES_HOUSE_API_KEY"), query="Brighton", max_results=100)
            directory_candidates.extend(res.records)
            source_health.append(res.__dict__)

        if "json_ld" in by_key:
            res = jsonld.directory(by_key["json_ld"].get("websites", []))
            directory_candidates.extend(res.records)
            source_health.append(res.__dict__)

    d_manifest = process_directory(directory_candidates, cfg, out_dir)

    # Event candidates
    event_candidates = []
    event_file = cfg["events"]["fixture_csv"] if fixtures else cfg["events"]["manual_csv"]
    res = manual.events(event_file)
    event_candidates.extend(res.records)
    source_health.append(res.__dict__)

    if not offline:
        registry = load_yaml(cfg["events"]["source_registry"])
        configured = _event_sources(registry)

        # Mature Lewes pattern: traverse first-party event/detail pages and parse both
        # JSON-LD and visible date-bearing event sections. JSON-LD-only extraction remains
        # as a secondary source so structured pages are not a single point of failure.
        res = structured_pages.harvest(
            configured,
            timeout=int((registry.get("harvest") or {}).get("timeout_seconds", 20)),
            max_links_per_source=int((registry.get("harvest") or {}).get("max_links_per_source", 30)),
        )
        event_candidates.extend(res.records)
        source_health.append(res.__dict__)

        res = jsonld.events(configured)
        event_candidates.extend(res.records)
        source_health.append(res.__dict__)

    if not offline:
        event_candidates = geocode_records(event_candidates)

    e_manifest = process_events(event_candidates, cfg, out_dir)

    _write_json(
        out_dir / "source-health.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "offline": offline,
            "fixtures": fixtures,
            "sources": source_health,
        },
    )

    # Fixtures are safe to install for deterministic CI/browser tests.  A live harvest
    # never overwrites public_html here; scripts/promote_release.py is the only live
    # promotion path after the coverage/release gate has passed.
    if offline or fixtures:
        install_public_feeds(out_dir, Path(cfg["outputs"]["public_html_data"]))
    return {"directory": d_manifest, "events": e_manifest, "source_health": source_health}
