from __future__ import annotations
import os
from datetime import datetime, timezone
import requests
from .base import AdapterResult

def discover(api_key: str | None, query: str = "Brighton", max_results: int = 100, timeout=30) -> AdapterResult:
    api_key=api_key or os.getenv("COMPANIES_HOUSE_API_KEY")
    if not api_key:
        return AdapterResult("companies_house",True,[],"credential absent; adapter skipped")
    try:
        r=requests.get(
            "https://api.company-information.service.gov.uk/search/companies",
            params={"q":query,"items_per_page":min(max_results,100)},
            auth=(api_key,""),timeout=timeout,headers={"User-Agent":"BrightonLive/0.1"}
        )
        r.raise_for_status()
        data=r.json()
    except Exception as exc:
        return AdapterResult("companies_house",False,[],str(exc))
    now=datetime.now(timezone.utc).isoformat(); records=[]
    for item in data.get("items",[])[:max_results]:
        addr=item.get("address") or {}
        records.append({
            "name":item.get("title",""),
            "category":"Professional Services",
            "address":" ".join(filter(None,[addr.get("premises"),addr.get("address_line_1"),addr.get("address_line_2"),addr.get("locality")])),
            "postcode":addr.get("postal_code",""),
            "website":"","phone":"","email":"",
            "address_public":False,"phone_public":False,"email_public":False,
            "manual_verified":False,"registered_office_only":True,
            "operational_location_confirmed":False,
            "company_number":item.get("company_number",""),
            "company_registered_office":addr,
            "evidence":[{
                "source_key":"companies_house",
                "source_url":f"https://find-and-update.company-information.service.gov.uk/company/{item.get('company_number','')}",
                "source_owner":"Companies House",
                "source_type":"authoritative_corporate","retrieved_at":now,"authoritative":True,
                "fields":["legal_name","company_number","registered_office"]
            }]
        })
    return AdapterResult("companies_house",True,records,f"{len(records)} corporate candidates (review only)")
