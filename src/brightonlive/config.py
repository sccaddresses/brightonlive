from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml

def load_yaml(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}

def load_project(path: str | Path = "config/brighton.yaml") -> dict[str, Any]:
    cfg = load_yaml(path)
    for section in ("project", "location", "outputs", "policy", "directory", "events"):
        if section not in cfg:
            raise ValueError(f"Missing required config section: {section}")
    return cfg
