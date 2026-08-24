from __future__ import annotations
from datetime import datetime, timezone
import requests
from icalendar import Calendar
from .base import AdapterResult

def _iso(v):
    if not v: return ""
    value=v.dt
    return value.isoformat() if hasattr(value,"isoformat") else str(value)

def harvest(calendars: list[dict], timeout=20) -> AdapterResult:
    records=[]; errors=[]; now=datetime.now(timezone.utc).isoformat()
    for src in calendars:
        try:
            r=requests.get(src["url"],timeout=timeout,headers={"User-Agent":"BrightonLive/0.1"})
            r.raise_for_status(); cal=Calendar.from_ical(r.content)
            for comp in cal.walk("VEVENT"):
                records.append({
                    "title":str(comp.get("summary","")),"start":_iso(comp.get("dtstart")),"end":_iso(comp.get("dtend")),
                    "venue":str(comp.get("location","")) or src.get("default_venue",""),
                    "address":"","postcode":src.get("default_postcode",""),
                    "latitude":src.get("default_latitude"),"longitude":src.get("default_longitude"),
                    "category":src.get("default_category","Uncategorised"),
                    "website":str(comp.get("url","")),"booking_url":"",
                    "source_url":str(comp.get("url","")) or src["url"],"source_owner":src.get("name") or src["url"],
                    "manual_verified":False,
                    "evidence":[{
                        "source_key":src.get("key","ics"),"source_url":src["url"],
                        "source_owner":src.get("name") or src["url"],"source_type":src.get("source_type","first_party"),
                        "retrieved_at":now,"fields":["title","start","end","location","url"]
                    }]
                })
        except Exception as exc:
            errors.append(f"{src['url']}: {exc}")
    return AdapterResult("ics",not errors,records,"; ".join(errors) or f"{len(records)} ICS candidates")
