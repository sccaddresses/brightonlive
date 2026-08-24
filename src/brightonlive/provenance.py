from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable

@dataclass(frozen=True)
class Evidence:
    source_key: str
    source_url: str
    source_owner: str
    source_type: str
    retrieved_at: str
    fields: tuple[str, ...] = ()
    authoritative: bool = False
    organisation_owned: bool = False

    def to_dict(self) -> dict:
        d = asdict(self)
        d["fields"] = list(self.fields)
        return d

def evidence_domains(evidence: Iterable[dict]) -> set[str]:
    from .common import domain_of
    return {domain_of(e.get("source_url")) for e in evidence if domain_of(e.get("source_url"))}

def provenance_complete(record: dict) -> bool:
    ev = record.get("evidence") or []
    if not ev:
        return False
    required = ("source_key", "source_url", "source_owner", "source_type", "retrieved_at")
    return all(all(item.get(k) for k in required) for item in ev)
