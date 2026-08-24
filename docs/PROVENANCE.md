# Provenance model

Evidence belongs to the record, not just to the scraper log.

Each evidence item contains:

```json
{
  "source_key": "brighton_dome",
  "source_url": "https://brightondome.org/whats-on/",
  "source_owner": "Brighton Dome",
  "source_type": "first_party",
  "retrieved_at": "2026-08-23T12:00:00+00:00",
  "fields": ["title", "start", "venue", "website"]
}
```

## Field-level principle

Where practical, `fields` records what the source actually supports. A company register can
support legal name/company number while not supporting the claim that an address is a consumer
trading location.

## Images

Production image records should additionally retain:
- original source URL / supplied-by identity;
- creator;
- licence/permission basis;
- retrieval date;
- original SHA-256;
- optimised-file SHA-256;
- associated place/event ID;
- alt text;
- publication approval.

The current website photography credits remain in `public_html/CREDITS.txt`.
