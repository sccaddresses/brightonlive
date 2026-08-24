# Architecture

BrightonLive is one product with deliberately separated layers.

## 1. Discovery

Source adapters create **candidate** directory/event records and evidence objects.
Candidates may be incomplete, duplicated or unsuitable for publication.

## 2. Provenance

Each candidate carries one or more evidence entries containing source key, source URL,
source owner, source type, retrieval time and fields supported by that evidence.

## 3. Normalisation / entity resolution

Directory records are resolved using high-value deterministic identifiers before fuzzy
matching: company number, website domain, telephone, postcode + similar name, then very
high-confidence name matching.

Different physical branches are not collapsed simply because they share a domain or company
number.

Events use title + date + venue/postcode fingerprints and merge source evidence for duplicate
records.

## 4. Privacy

Public/private flags are explicit. Registered offices, charity contact addresses and
service-provider administrative locations are not assumed to be public destinations.

## 5. Validation

Directory rules check required identity/category, postcodes, URLs, coordinates and contradictory
privacy flags.

Event rules check title, start time, location signal, source URL, postcode and coordinates.

## 6. Verification

A record is either:
- `publication_ready`
- `verification_pending`
- `held_for_review`

The decision is policy-driven and fail-closed.

## 7. Export

The pipeline writes:
- internal complete records;
- review queue;
- publication-safe JSON/GeoJSON and manifests.

Only publication-safe output is copied to `public_html/assets/data`.

## 8. Release gate

Coverage is assessed independently of per-record publication safety. A run can contain valid
records but still fail as a **replacement feed** if breadth, depth or source coverage is weak.

This protects against a transient source outage shrinking the live BrightonLive site.
