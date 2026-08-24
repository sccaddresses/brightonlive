from __future__ import annotations
import json
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from .base import AdapterResult

ORG_TYPES={"LocalBusiness","Organization","Restaurant","CafeOrCoffeeShop","BarOrPub","Store","Hotel","LodgingBusiness","TouristAttraction","EntertainmentBusiness","HealthAndBeautyBusiness"}
EVENT_TYPES={"Event","MusicEvent","TheaterEvent","Festival","BusinessEvent","SportsEvent","ExhibitionEvent"}

def _flatten(obj):
    if isinstance(obj,list):
        for item in obj: yield from _flatten(item)
    elif isinstance(obj,dict):
        if "@graph" in obj:
            yield from _flatten(obj["@graph"])
        else:
            yield obj

def fetch_jsonld(url: str, timeout=15) -> list[dict]:
    r=requests.get(url,timeout=timeout,headers={"User-Agent":"BrightonLive/0.1 (+https://brightonlive.uk/)"})
    r.raise_for_status()
    soup=BeautifulSoup(r.text,"html.parser")
    out=[]
    for tag in soup.find_all("script",attrs={"type":"application/ld+json"}):
        try:
            out.extend(_flatten(json.loads(tag.string or tag.get_text() or "{}")))
        except json.JSONDecodeError:
            continue
    return list(out)

def directory(websites: list[str], timeout=15) -> AdapterResult:
    records=[]; failures=[]
    now=datetime.now(timezone.utc).isoformat()
    for url in websites:
        try:
            for obj in fetch_jsonld(url,timeout):
                types=obj.get("@type",[])
                if isinstance(types,str): types=[types]
                if not set(types).intersection(ORG_TYPES): continue
                address=obj.get("address") or {}
                geo=obj.get("geo") or {}
                record={
                    "name":obj.get("name",""),
                    "category":next(iter(set(types).intersection(ORG_TYPES)), "Organization"),
                    "address":address.get("streetAddress","") if isinstance(address,dict) else "",
                    "postcode":address.get("postalCode","") if isinstance(address,dict) else "",
                    "latitude":geo.get("latitude") if isinstance(geo,dict) else None,
                    "longitude":geo.get("longitude") if isinstance(geo,dict) else None,
                    "website":obj.get("url") or url,
                    "phone":obj.get("telephone",""),
                    "email":obj.get("email",""),
                    "address_public":True,"phone_public":True,"email_public":True,
                    "manual_verified":False,"operational_location_confirmed":True,
                    "evidence":[{
                        "source_key":"json_ld","source_url":url,"source_owner":obj.get("name") or url,
                        "source_type":"owned_primary","retrieved_at":now,"organisation_owned":True,
                        "fields":["name","address","postcode","website","telephone","geo"]
                    }]
                }
                records.append(record)
        except Exception as exc:
            failures.append(f"{url}: {exc}")
    return AdapterResult("json_ld",not failures,records,"; ".join(failures) or f"{len(records)} JSON-LD organisations")

def events(urls: list[dict], timeout=15) -> AdapterResult:
    records=[]; failures=[]; now=datetime.now(timezone.utc).isoformat()
    for src in urls:
        url=src["url"]; owner=src.get("name") or url
        try:
            for obj in fetch_jsonld(url,timeout):
                types=obj.get("@type",[])
                if isinstance(types,str): types=[types]
                if not set(types).intersection(EVENT_TYPES): continue
                loc=obj.get("location") or {}
                addr=loc.get("address") if isinstance(loc,dict) else {}
                if not isinstance(addr,dict): addr={}
                geo=loc.get("geo") if isinstance(loc,dict) else {}
                if not isinstance(geo,dict): geo={}
                records.append({
                    "title":obj.get("name",""),
                    "start":obj.get("startDate",""),
                    "end":obj.get("endDate",""),
                    "venue":loc.get("name","") if isinstance(loc,dict) else str(loc or ""),
                    "address":addr.get("streetAddress",""),
                    "postcode":addr.get("postalCode",""),
                    "latitude":geo.get("latitude"),
                    "longitude":geo.get("longitude"),
                    "category":"Uncategorised",
                    "website":obj.get("url") or url,
                    "booking_url":(obj.get("offers") or {}).get("url","") if isinstance(obj.get("offers"),dict) else "",
                    "source_url":obj.get("url") or url,
                    "source_owner":owner,
                    "manual_verified":False,
                    "evidence":[{
                        "source_key":src.get("key","structured"),
                        "source_url":url,"source_owner":owner,"source_type":src.get("source_type","first_party"),
                        "retrieved_at":now,"organisation_owned":True,
                        "fields":["title","start","end","venue","website","booking_url"]
                    }]
                })
        except Exception as exc:
            failures.append(f"{url}: {exc}")
    return AdapterResult("json_ld_events",not failures,records,"; ".join(failures) or f"{len(records)} JSON-LD events")
