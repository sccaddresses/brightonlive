from __future__ import annotations
from .common import normalize_name

def build_alias_map(items: list[dict]) -> dict[str, str]:
    out = {}
    for item in items:
        canonical = item["name"]
        out[normalize_name(canonical)] = canonical
        for alias in item.get("aliases", []):
            out[normalize_name(alias)] = canonical
    return out

def normalise_category(value: str, items: list[dict], fallback: str = "Uncategorised") -> str:
    aliases = build_alias_map(items)
    n = normalize_name(value)
    if n in aliases:
        return aliases[n]
    # substring fallback for source labels such as "live music venue".
    matches = [(len(k), v) for k, v in aliases.items() if k and k in n]
    return max(matches)[1] if matches else (value.strip() or fallback)
