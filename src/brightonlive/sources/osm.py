from __future__ import annotations
from datetime import datetime, timezone
import requests
from .base import AdapterResult

def harvest(endpoint: str, lat: float, lon: float, radius_km: float, timeout=45) -> AdapterResult:
    radius=int(radius_km*1000)
    query=f'''
[out:json][timeout:40];
(
  nwr(around:{radius},{lat},{lon})["name"]["amenity"];
  nwr(around:{radius},{lat},{lon})["name"]["shop"];
  nwr(around:{radius},{lat},{lon})["name"]["tourism"];
  nwr(around:{radius},{lat},{lon})["name"]["leisure"];
  nwr(around:{radius},{lat},{lon})["name"]["office"];
);
out center tags;
'''
    try:
        r=requests.post(endpoint,data={"data":query},timeout=timeout,headers={"User-Agent":"BrightonLive/0.1"})
        r.raise_for_status()
        data=r.json()
    except Exception as exc:
        return AdapterResult("osm",False,[],str(exc))

    now=datetime.now(timezone.utc).isoformat()
    records=[]
    for el in data.get("elements",[]):
        tags=el.get("tags",{})
        name=tags.get("name")
        if not name: continue
        center=el.get("center",{})
        latv=el.get("lat",center.get("lat")); lonv=el.get("lon",center.get("lon"))
        category=tags.get("amenity") or tags.get("shop") or tags.get("tourism") or tags.get("leisure") or tags.get("office") or "place"
        source_url=f"https://www.openstreetmap.org/{el.get('type')}/{el.get('id')}"
        records.append({
            "name":name,"category":category,
            "address":" ".join(filter(None,[tags.get("addr:housenumber"),tags.get("addr:street")])),
            "postcode":tags.get("addr:postcode",""),
            "latitude":latv,"longitude":lonv,
            "website":tags.get("website") or tags.get("contact:website") or "",
            "phone":tags.get("phone") or tags.get("contact:phone") or "",
            "email":tags.get("email") or tags.get("contact:email") or "",
            "address_public":True,"phone_public":True,"email_public":True,
            "manual_verified":False,"operational_location_confirmed":False,
            "osm_id":f"{el.get('type')}/{el.get('id')}",
            "evidence":[{
                "source_key":"osm","source_url":source_url,"source_owner":"OpenStreetMap contributors",
                "source_type":"community_open_data","retrieved_at":now,
                "fields":["name","category","address","postcode","geo","website"]
            }]
        })
    return AdapterResult("osm",True,records,f"{len(records)} OSM candidates")
