from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import json

def _load(path):
    p=Path(path)
    if not p.exists(): return []
    obj=json.loads(p.read_text(encoding="utf-8"))
    return obj.get("records",obj if isinstance(obj,list) else [])

def directory_metrics(records):
    n=len(records) or 1
    cats=Counter(r.get("category","") for r in records)
    return {
        "count":len(records),
        "website_coverage":sum(bool(r.get("website")) for r in records)/n,
        "contact_coverage":sum(bool(r.get("phone") or r.get("email") or r.get("website")) for r in records)/n,
        "geocoded_coverage":sum(r.get("latitude") not in (None,"") and r.get("longitude") not in (None,"") for r in records)/n,
        "multi_source_coverage":sum(len(r.get("sources",[]))>=2 for r in records)/n,
        "categories_with_5_records":sum(v>=5 for v in cats.values()),
    }

def event_metrics(records):
    n=len(records) or 1
    return {
        "count":len(records),
        "primary_source_coverage":sum(bool(r.get("source_url") or r.get("sources")) for r in records)/n,
        "venue_signal_coverage":sum(bool(r.get("venue") or r.get("postcode") or r.get("latitude")) for r in records)/n,
        "geocoded_coverage":sum(r.get("latitude") not in (None,"") and r.get("longitude") not in (None,"") for r in records)/n,
    }

def release_report(cfg, exports_root):
    exports_root=Path(exports_root)
    d=_load(exports_root/"directory/public/directory.v1.json")
    e=_load(exports_root/"events/public/events.v1.json")
    dm=directory_metrics(d); em=event_metrics(e)
    dg=cfg["policy"]["directory_coverage"]; eg=cfg["policy"]["event_coverage"]
    checks={
      "directory_minimum_publish_safe": dm["count"]>=dg["minimum_publish_safe"],
      "directory_category_depth": dm["categories_with_5_records"]>=dg["minimum_priority_categories_with_5_records"],
      "directory_website_coverage": dm["website_coverage"]>=dg["minimum_website_coverage"],
      "directory_contact_coverage": dm["contact_coverage"]>=dg["minimum_contact_coverage"],
      "directory_geocoded_coverage": dm["geocoded_coverage"]>=dg["minimum_geocoded_coverage"],
      "directory_multi_source_coverage": dm["multi_source_coverage"]>=dg["minimum_multi_source_coverage"],
      "events_minimum_upcoming": em["count"]>=eg["minimum_upcoming_events"],
      "events_source_coverage": em["primary_source_coverage"]>=eg["minimum_primary_source_coverage"],
      "events_venue_signal": em["venue_signal_coverage"]>=eg["minimum_venue_signal_coverage"],
      "events_geocoded": em["geocoded_coverage"]>=eg["minimum_geocoded_coverage"],
    }
    return {
      "generated_at":datetime.now(timezone.utc).isoformat(),
      "release_ready":all(checks.values()),
      "checks":checks,"directory":dm,"events":em,
    }
