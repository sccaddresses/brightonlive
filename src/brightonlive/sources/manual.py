from __future__ import annotations
import csv
from pathlib import Path
from datetime import datetime, timezone
from .base import AdapterResult
from brightonlive.common import parse_bool, normalize_postcode

def _rows(path):
    p=Path(path)
    if not p.exists():
        return []
    with p.open("r",encoding="utf-8-sig",newline="") as fh:
        return list(csv.DictReader(fh))

def directory(path: str, source_key="manual") -> AdapterResult:
    records=[]
    now=datetime.now(timezone.utc).isoformat()
    for row in _rows(path):
        if not (row.get("name") or "").strip():
            continue
        record=dict(row)
        for k in ("latitude","longitude"):
            if record.get(k):
                try: record[k]=float(record[k])
                except ValueError: pass
        record["postcode"]=normalize_postcode(record.get("postcode"))
        for k,default in (("address_public",True),("phone_public",True),("email_public",True),("manual_verified",False)):
            record[k]=parse_bool(record.get(k),default)
        url=record.get("source_url") or record.get("website") or "manual://reviewed"
        owner=record.get("source_owner") or "Manual review"
        record["evidence"]=[{
            "source_key":source_key,"source_url":url,"source_owner":owner,
            "source_type":"human_review","retrieved_at":now,
            "fields":["name","category","address","postcode","website","phone","email"]
        }]
        record["operational_location_confirmed"]=bool(record.get("address") and record["manual_verified"])
        records.append(record)
    return AdapterResult(source_key,True,records,f"{len(records)} manual directory records")

def events(path: str, source_key="manual_events") -> AdapterResult:
    records=[]
    now=datetime.now(timezone.utc).isoformat()
    for row in _rows(path):
        if not (row.get("title") or "").strip():
            continue
        record=dict(row)
        for k in ("latitude","longitude"):
            if record.get(k):
                try: record[k]=float(record[k])
                except ValueError: pass
        record["postcode"]=normalize_postcode(record.get("postcode"))
        record["manual_verified"]=parse_bool(record.get("manual_verified"),False)
        url=record.get("source_url") or record.get("website") or "manual://reviewed"
        owner=record.get("source_owner") or "Manual review"
        record["evidence"]=[{
            "source_key":source_key,"source_url":url,"source_owner":owner,
            "source_type":"human_review","retrieved_at":now,
            "fields":["title","start","end","venue","location","website","booking_url"]
        }]
        records.append(record)
    return AdapterResult(source_key,True,records,f"{len(records)} manual event records")
