from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json

def _write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def _geojson(records: list[dict]) -> dict:
    features = []
    for r in records:
        if r.get("latitude") in (None, "") or r.get("longitude") in (None, ""):
            continue
        props = {k: v for k, v in r.items() if k not in {"latitude", "longitude"}}
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(r["longitude"]), float(r["latitude"])]},
            "properties": props,
        })
    return {"type": "FeatureCollection", "features": features}

def export_directory(internal, public, review, out_dir, cfg):
    base = Path(out_dir) / "directory"
    _write(base/"internal"/"listings.json", internal)
    _write(base/"review"/"review-queue.json", review)
    _write(base/"public"/"directory.v1.json", {"version":"1","records":public})
    _write(base/"public"/"directory.v1.geojson", _geojson(public))
    manifest = {
        "schema_version": "1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "internal_count": len(internal),
        "public_count": len(public),
        "review_count": len(review),
    }
    _write(base/"public"/"manifest.v1.json", manifest)
    return manifest
