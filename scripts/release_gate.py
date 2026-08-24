import argparse, json
from pathlib import Path
from brightonlive.config import load_project
from brightonlive.coverage import release_report

p=argparse.ArgumentParser()
p.add_argument("--config",default="config/brighton.yaml")
p.add_argument("--strict",action="store_true")
args=p.parse_args()
cfg=load_project(args.config)
report=release_report(cfg,cfg["outputs"]["directory"])
path=Path(cfg["outputs"]["directory"])/"release-report.json"
path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2))
if args.strict and not report["release_ready"]:
    raise SystemExit(2)
