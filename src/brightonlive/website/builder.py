from __future__ import annotations
from pathlib import Path
import json, shutil

def install_public_feeds(exports_root: str | Path, public_data: str | Path) -> None:
    exports_root=Path(exports_root); public_data=Path(public_data)
    public_data.mkdir(parents=True,exist_ok=True)
    mapping={
        exports_root/"directory/public/directory.v1.json": public_data/"directory.v1.json",
        exports_root/"directory/public/directory.v1.geojson": public_data/"directory.v1.geojson",
        exports_root/"directory/public/manifest.v1.json": public_data/"directory-manifest.v1.json",
        exports_root/"events/public/events.v1.json": public_data/"events.v1.json",
        exports_root/"events/public/events.v1.geojson": public_data/"events.v1.geojson",
        exports_root/"events/public/manifest.v1.json": public_data/"events-manifest.v1.json",
    }
    for src,dst in mapping.items():
        if src.exists():
            shutil.copy2(src,dst)
