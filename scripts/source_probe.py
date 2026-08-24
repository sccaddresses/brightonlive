import argparse, json, time
from pathlib import Path
import requests
from brightonlive.config import load_yaml
from datetime import datetime, timezone

p=argparse.ArgumentParser()
p.add_argument("--directory-registry",default="config/directory-sources.yaml")
p.add_argument("--event-registry",default="config/event-sources.yaml")
p.add_argument("--output",default="exports/brighton/source-probes.json")
args=p.parse_args()

urls=[]
d=load_yaml(args.directory_registry)
for src in d.get("sources",[]):
    for key in ("endpoint","index_url"):
        if src.get(key): urls.append((src.get("key"),src[key]))
for item in d.get("discovery_pages",[]):
    if item.get("url"): urls.append((item.get("name"),item["url"]))

e=load_yaml(args.event_registry)
for src in e.get("suppliers",[]):
    for _,url in (src.get("urls") or {}).items():
        urls.append((src.get("key"),url))

seen=set(); results=[]
headers={"User-Agent":"BrightonLive-SourceProbe/0.1 (+https://brightonlive.uk/)"}
for key,url in urls:
    if url in seen: continue
    seen.add(url)
    started=time.monotonic()
    try:
        r=requests.get(url,headers=headers,timeout=12,allow_redirects=True)
        results.append({"key":key,"url":url,"status":r.status_code,"final_url":r.url,"ok":r.status_code<400,"elapsed_ms":round((time.monotonic()-started)*1000)})
    except Exception as exc:
        results.append({"key":key,"url":url,"ok":False,"error":str(exc),"elapsed_ms":round((time.monotonic()-started)*1000)})
out={"generated_at":datetime.now(timezone.utc).isoformat(),"results":results}
path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2))
