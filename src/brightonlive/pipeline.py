from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json, os

from .config import load_project, load_yaml
from .sources import manual, jsonld, osm, fhrs, companies_house
from .directory.pipeline import process_directory
from .events.pipeline import process_events
from .website.builder import install_public_feeds

def _write_json(path, obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def _event_sources(registry: dict) -> list[dict]:
    out=[]
    for s in registry.get("suppliers",[]):
        if not s.get("enabled",False): continue
        url=(s.get("urls") or {}).get("events") or (s.get("urls") or {}).get("website")
        if url:
            out.append({
                "key":s["key"],"name":s["name"],"url":url,
                "source_type":s.get("source_class","first_party"),
            })
    return out

def run(config_path="config/brighton.yaml", offline=False, fixtures=False) -> dict:
    cfg=load_project(config_path)
    out_dir=Path(cfg["outputs"]["directory"])
    out_dir.mkdir(parents=True,exist_ok=True)
    source_health=[]

    # Directory candidates
    directory_candidates=[]
    directory_file=cfg["directory"]["fixture_csv"] if fixtures else cfg["directory"]["manual_csv"]
    res=manual.directory(directory_file)
    directory_candidates.extend(res.records); source_health.append(res.__dict__)

    if not offline:
        registry=load_yaml(cfg["directory"]["source_registry"])
        by_key={s["key"]:s for s in registry.get("sources",[]) if s.get("enabled")}
        loc=cfg["location"]

        if "fhrs" in by_key:
            s=by_key["fhrs"]
            res=fhrs.harvest(s["endpoint"],loc["latitude"],loc["longitude"],loc["radius_miles"])
            directory_candidates.extend(res.records); source_health.append(res.__dict__)

        if "osm" in by_key:
            s=by_key["osm"]
            res=osm.harvest(s["endpoint"],loc["latitude"],loc["longitude"],loc["radius_km"])
            directory_candidates.extend(res.records); source_health.append(res.__dict__)

        if "companies_house" in by_key:
            res=companies_house.discover(os.getenv("COMPANIES_HOUSE_API_KEY"),query="Brighton",max_results=100)
            directory_candidates.extend(res.records); source_health.append(res.__dict__)

        if "json_ld" in by_key:
            res=jsonld.directory(by_key["json_ld"].get("websites",[]))
            directory_candidates.extend(res.records); source_health.append(res.__dict__)

    d_manifest=process_directory(directory_candidates,cfg,out_dir)

    # Event candidates
    event_candidates=[]
    event_file=cfg["events"]["fixture_csv"] if fixtures else cfg["events"]["manual_csv"]
    res=manual.events(event_file)
    event_candidates.extend(res.records); source_health.append(res.__dict__)

    if not offline:
        registry=load_yaml(cfg["events"]["source_registry"])
        structured=_event_sources(registry)
        res=jsonld.events(structured)
        event_candidates.extend(res.records); source_health.append(res.__dict__)

    e_manifest=process_events(event_candidates,cfg,out_dir)

    _write_json(out_dir/"source-health.json",{
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "offline":offline,"fixtures":fixtures,"sources":source_health
    })
    install_public_feeds(out_dir,Path(cfg["outputs"]["public_html_data"]))
    return {"directory":d_manifest,"events":e_manifest,"source_health":source_health}
