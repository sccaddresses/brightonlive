from __future__ import annotations
from datetime import datetime, timezone
import feedparser
from .base import AdapterResult

def harvest(feeds: list[dict]) -> AdapterResult:
    records=[]; errors=[]; now=datetime.now(timezone.utc).isoformat()
    for feed in feeds:
        parsed=feedparser.parse(feed["url"])
        if getattr(parsed,"bozo",False):
            errors.append(f"{feed['url']}: {parsed.bozo_exception}")
        for entry in parsed.entries:
            start=entry.get("published") or entry.get("updated") or ""
            records.append({
                "title":entry.get("title",""),"start":start,"end":"",
                "venue":feed.get("default_venue",""),"address":"","postcode":feed.get("default_postcode",""),
                "latitude":feed.get("default_latitude"),"longitude":feed.get("default_longitude"),
                "category":feed.get("default_category","Uncategorised"),
                "website":entry.get("link",""),"booking_url":"","source_url":entry.get("link") or feed["url"],
                "source_owner":feed.get("name") or feed["url"],"manual_verified":False,
                "evidence":[{
                    "source_key":feed.get("key","rss"),"source_url":feed["url"],
                    "source_owner":feed.get("name") or feed["url"],"source_type":feed.get("source_type","first_party"),
                    "retrieved_at":now,"fields":["title","date","url"]
                }]
            })
    return AdapterResult("rss",not errors,records,"; ".join(errors) or f"{len(records)} RSS candidates")
