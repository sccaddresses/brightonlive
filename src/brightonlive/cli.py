from __future__ import annotations
import argparse, json
from .pipeline import run
from .config import load_project
from .coverage import release_report
from .locality import lookup_uk_postcode


def main(argv=None):
    p = argparse.ArgumentParser(prog="brightonlive")
    sub = p.add_subparsers(dest="cmd", required=True)

    runp = sub.add_parser("run")
    runp.add_argument("--config", default="config/brighton.yaml")
    runp.add_argument("--offline", action="store_true")
    runp.add_argument("--fixtures", action="store_true")

    sub.add_parser("offline")

    gate = sub.add_parser("release-report")
    gate.add_argument("--config", default="config/brighton.yaml")

    postcode = sub.add_parser("postcode-lookup", help="Resolve a UK postcode for a future locality profile")
    postcode.add_argument("postcode")

    args = p.parse_args(argv)
    if args.cmd == "offline":
        result = run("config/brighton.yaml", offline=True, fixtures=True)
        print(json.dumps(result, indent=2))
        return 0
    if args.cmd == "run":
        result = run(args.config, offline=args.offline, fixtures=args.fixtures)
        print(json.dumps(result, indent=2))
        return 0
    if args.cmd == "release-report":
        cfg = load_project(args.config)
        report = release_report(cfg, cfg["outputs"]["directory"])
        print(json.dumps(report, indent=2))
        return 0 if report["release_ready"] else 2
    if args.cmd == "postcode-lookup":
        print(json.dumps(lookup_uk_postcode(args.postcode), indent=2))
        return 0
    return 1
