from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AdapterResult:
    key: str
    ok: bool
    records: list[dict] = field(default_factory=list)
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
