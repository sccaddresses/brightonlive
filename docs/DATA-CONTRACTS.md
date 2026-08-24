# Public data contracts

## Directory

`public_html/assets/data/directory.v1.json`

```json
{"version":"1","records":[]}
```

Each record may include:
- `name`, `category`
- public `address`, `postcode`, `latitude`, `longitude`
- public `website`, `phone`, `email`
- stable source-derived IDs where safe
- `verification_status`
- `integrity_sha256`
- concise public `sources`

## Events

`public_html/assets/data/events.v1.json`

Each record may include:
- `title`, `start`, `end`
- `venue`, public location/geometry
- `category`
- `website`, `booking_url`
- `event_fingerprint`, `integrity_sha256`
- concise public `sources`

Internal evidence/review notes never form part of the browser contract.
