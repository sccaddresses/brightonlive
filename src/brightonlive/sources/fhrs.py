from __future__ import annotations
from datetime import datetime, timezone
import requests
from .base import AdapterResult

def harvest(endpoint: str, lat: float, lon: float, radius_miles: float, timeout=45) -> AdapterResult:
    headers={"x-api-version":"2","Accept":"application/json","User-Agent":"BrightonLive/0.1"}
    params={"latitude":lat,"longitude":lon,"maxDistanceLimit":radius_miles,"pageSize":5000}
    try:
        r=requests.get(endpoint,params=params,headers=headers,timeout=timeout)
        r.raise_for_status()
        data=r.json()
    except Exception as exc:
        return AdapterResult("fhrs",False,[],str(exc))
    now=datetime.now(timezone.utc).isoformat()
    records=[]
    for item in data.get("establishments",[]):
        address=" ".join(filter(None,[item.get("AddressLine1"),item.get("AddressLine2"),item.get("AddressLine3"),item.get("AddressLine4")]))
        records.append({
            "name":item.get("BusinessName",""),
            "category":item.get("BusinessType","Food & Drink"),
            "address":address,
            "postcode":item.get("PostCode",""),
            "latitude":(item.get("geocode") or {}).get("latitude"),
            "longitude":(item.get("geocode") or {}).get("longitude"),
            "website":"","phone":"","email":"",
            "address_public":True,"phone_public":False,"email_public":False,
            "manual_verified":False,"operational_location_confirmed":True,
            "fhrs_id":item.get("FHRSID"),
            "evidence":[{
                "source_key":"fhrs",
                "source_url":f"https://ratings.food.gov.uk/business/en-GB/{item.get('FHRSID','')}",
                "source_owner":"Food Standards Agency",
                "source_type":"authoritative_class_a","retrieved_at":now,"authoritative":True,
                "fields":["name","business_type","address","postcode","geo"]
            }]
        })
    return AdapterResult("fhrs",True,records,f"{len(records)} FHRS establishments")
