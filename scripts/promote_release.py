from pathlib import Path
import shutil

from brightonlive.config import load_project
from brightonlive.coverage import release_report
from brightonlive.website.builder import install_public_feeds

cfg = load_project("config/brighton.yaml")
exports = Path(cfg["outputs"]["directory"])
report = release_report(cfg, exports)
if not report["release_ready"]:
    raise SystemExit("Release gate failed; last-known-good publication not replaced.")

published = Path(cfg["outputs"]["published"])
published.mkdir(parents=True, exist_ok=True)
for rel in (
    "directory/public/directory.v1.json",
    "directory/public/directory.v1.geojson",
    "directory/public/manifest.v1.json",
    "events/public/events.v1.json",
    "events/public/events.v1.geojson",
    "events/public/manifest.v1.json",
):
    src = exports / rel
    dst = published / Path(rel).name
    shutil.copy2(src, dst)

# The public webroot is changed only here, after all release gates pass.
install_public_feeds(exports, Path(cfg["outputs"]["public_html_data"]))
print("Promoted governed feeds to", published, "and public_html/assets/data")
