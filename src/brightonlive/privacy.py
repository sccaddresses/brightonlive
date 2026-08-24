from __future__ import annotations

PRIVATE_KEYS = {
    "review_notes",
    "internal_notes",
    "raw_source",
    "company_registered_office",
    "private_contact_address",
}

def public_directory_record(record: dict) -> dict:
    out = {k: v for k, v in record.items() if k not in PRIVATE_KEYS}
    if not record.get("address_public", True):
        for k in ("address", "postcode", "latitude", "longitude"):
            out.pop(k, None)
    if not record.get("phone_public", True):
        out.pop("phone", None)
    if not record.get("email_public", True):
        out.pop("email", None)

    # Do not expose full internal evidence objects. Keep a concise public source trail.
    out["sources"] = [
        {
            "source_owner": e.get("source_owner"),
            "source_url": e.get("source_url"),
            "source_type": e.get("source_type"),
            "retrieved_at": e.get("retrieved_at"),
        }
        for e in record.get("evidence", [])
        if e.get("source_url")
    ]
    out.pop("evidence", None)
    return out
