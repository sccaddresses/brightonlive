import argparse, json, time
from pathlib import Path
from datetime import datetime, timezone

import requests

from brightonlive.config import load_yaml

p = argparse.ArgumentParser()
p.add_argument("--directory-registry", default="config/directory-sources.yaml")
p.add_argument("--event-registry", default="config/event-sources.yaml")
p.add_argument("--output", default="exports/brighton/source-probes.json")
args = p.parse_args()

headers = {"User-Agent": "BrightonLive-SourceProbe/0.2 (+https://brightonlive.uk/)"}
results = []
seen = set()


def record(key, url, method="GET", **kwargs):
    marker = (method, url)
    if marker in seen:
        return
    seen.add(marker)
    started = time.monotonic()
    try:
        request_headers = kwargs.pop("headers", headers)
        if method == "POST":
            response = requests.post(url, headers=request_headers, timeout=15, allow_redirects=True, **kwargs)
        else:
            response = requests.get(url, headers=request_headers, timeout=15, allow_redirects=True, **kwargs)
        results.append({
            "key": key,
            "url": url,
            "method": method,
            "status": response.status_code,
            "final_url": str(response.url),
            "ok": response.status_code < 400,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
        })
    except Exception as exc:
        results.append({
            "key": key,
            "url": url,
            "method": method,
            "ok": False,
            "error": str(exc),
            "elapsed_ms": round((time.monotonic() - started) * 1000),
        })


directory = load_yaml(args.directory_registry)
for src in directory.get("sources", []):
    if not src.get("enabled", False):
        continue
    key = src.get("key")
    endpoint = src.get("endpoint")
    if key == "fhrs" and endpoint:
        record(
            key,
            endpoint,
            params={"latitude": 50.8225, "longitude": -0.1372, "maxDistanceLimit": 1, "pageSize": 1},
            headers={**headers, "x-api-version": "2", "Accept": "application/json"},
        )
    elif key == "osm" and endpoint:
        record(key, endpoint, method="POST", data={"data": "[out:json][timeout:10];node(50.81,-0.15,50.82,-0.14)[name];out 1;"})
    else:
        for field in ("endpoint", "index_url"):
            if src.get(field):
                record(key, src[field])
for item in directory.get("discovery_pages", []):
    if item.get("url"):
        record(item.get("name"), item["url"])

events = load_yaml(args.event_registry)
for src in events.get("suppliers", []):
    if not src.get("enabled", False):
        continue
    for url in (src.get("urls") or {}).values():
        record(src.get("key"), url)

out = {"generated_at": datetime.now(timezone.utc).isoformat(), "results": results}
path = Path(args.output)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2))
