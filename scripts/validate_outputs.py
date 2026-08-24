import argparse, json
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("--exports-dir",default="exports/brighton")
p.add_argument("--allow-empty",action="store_true")
args=p.parse_args()
root=Path(args.exports_dir)
paths=[
 root/"directory/public/directory.v1.json",
 root/"events/public/events.v1.json",
 root/"directory/review/review-queue.json",
 root/"events/review/review-queue.json",
 root/"source-health.json",
]
missing=[str(x) for x in paths if not x.exists()]
if missing:
    raise SystemExit("Missing outputs: "+", ".join(missing))
d=json.loads(paths[0].read_text(encoding="utf-8")).get("records",[])
e=json.loads(paths[1].read_text(encoding="utf-8")).get("records",[])
if not args.allow_empty and (not d or not e):
    raise SystemExit("Public output empty")
print(f"PASS: directory={len(d)} events={len(e)}")
