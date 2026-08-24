from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json

INTERNAL_ONLY = {"review_notes", "raw_source"}

def _public_record(r: dict) -> dict:
    out = {k:v for k,v in r.items() if k not in INTERNAL_ONLY}
    out["sources"] = [
        {
            "source_owner": e.get("source_owner"),
            "source_url": e.get("source_url"),
            "source_type": e.get("source_type"),
            "retrieved_at": e.get("retrieved_at"),
        }
        for e in r.get("evidence", [])
    ]
    out.pop("evidence", None)
    return out

def _write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def _geojson(records: list[dict]) -> dict:
    feats=[]
    for r in records:
        if r.get("latitude") in (None,"") or r.get("longitude") in (None,""):
            continue
        props={k:v for k,v in _public_record(r).items() if k not in {"latitude","longitude"}}
        feats.append({"type":"Feature","geometry":{"type":"Point","coordinates":[float(r["longitude"]),float(r["latitude"])]},"properties":props})
    return {"type":"FeatureCollection","features":feats}

def export_events(internal, public, review, out_dir, cfg):
    base=Path(out_dir)/"events"
    public_clean=[_public_record(r) for r in public]
    _write(base/"internal"/"events.json", internal)
    _write(base/"review"/"review-queue.json", review)
    _write(base/"public"/"events.v1.json", {"version":"1","records":public_clean})
    _write(base/"public"/"events.v1.geojson", _geojson(public))
    manifest={
        "schema_version":"1",
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "internal_count":len(internal),
        "public_count":len(public),
        "review_count":len(review),
    }
    _write(base/"public"/"manifest.v1.json",manifest)
    return manifest
