# BrightonLive

**BrightonLive** is a map-first local information platform for Brighton & Hove.

This repository deliberately combines the three layers that proved useful in the existing
Lewes ecosystem:

- a **public local guide** in the style of LewesLive;
- a reusable **directory harvesting / entity-resolution engine**;
- a reusable **events discovery / provenance / validation engine**.

It is a monorepo for one product, not one giant script. Website, directory, events, source
adapters, governance, tests and deployment are separated into modules but versioned together.

## Product principle

BrightonLive should feel like a useful Brighton website to the public.

The evidence machinery stays behind the interface:

> **discover → retain provenance → normalise → deduplicate → validate → verify → publish**

A harvested candidate is **never** a public listing merely because it was found.

Every publishable directory or event record must carry:

1. **Provenance** — where the relevant facts came from and when they were retrieved.
2. **Integrity** — stable IDs, deterministic fingerprints/hashes and change history.
3. **Validation** — required fields and deterministic format/range checks.
4. **Verification** — a defined evidence decision that permits or blocks publication.

Failures go to the review queue. They do not leak into `public_html`.

## Repository layout

```text
BrightonLive/
├─ public_html/                  client-facing BrightonLive site
│  └─ assets/data/              generated publication-safe feeds only
├─ src/brightonlive/
│  ├─ directory/                entity resolution, taxonomy, directory pipeline/export
│  ├─ events/                   event normalisation, dedupe, pipeline/export
│  ├─ sources/                  source adapters
│  └─ website/                  site-feed integration/build helpers
├─ config/
│  ├─ brighton.yaml             main product/release policy
│  ├─ directory-sources.yaml    directory source registry
│  ├─ event-sources.yaml        Brighton event supplier registry
│  └─ taxonomy.yaml             shared categories
├─ data/
│  ├─ manual/                   explicit human-reviewed corrections/submissions
│  ├─ fixtures/                 deterministic test data only
│  └─ cache/                    ignored runtime cache
├─ exports/brighton/            generated internal/review/public output
├─ published/brighton/          optional last-known-good governed feeds
├─ scripts/                     validation, probing, release and repo utilities
├─ docs/                        architecture, evidence, privacy, deployment and operations
├─ ops/                         runbooks
├─ tests/                       deterministic test suite
└─ .github/workflows/           CI, weekly data run and manual deployment
```

## Quick start — Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python run.py offline
pytest
```

The offline run uses fixture/manual data only and performs no network requests.

## Live Brighton data run

```powershell
python run.py run --config config/brighton.yaml
```

Optional source credentials are documented in `.env.example` and `docs/SECRETS.md`.

## Outputs

A normal run creates:

```text
exports/brighton/
  directory/
    internal/listings.json
    review/review-queue.json
    public/directory.v1.json
    public/directory.v1.geojson
    public/manifest.v1.json
  events/
    internal/events.json
    review/review-queue.json
    public/events.v1.json
    public/events.v1.geojson
    public/manifest.v1.json
  source-health.json
  release-report.json
```

Only the `public/` contracts are copied into:

```text
public_html/assets/data/
```

Internal provenance evidence, suppressed address/contact data and review notes never need to
be placed under the web root.

## Publication logic

Directory records may become publication-ready when core validation passes **and** one of the
configured verification conditions applies, for example:

- explicitly manually verified;
- a suitable authoritative Class A source for that entity type;
- two independent sources corroborate the same operational entity;
- organisation-owned structured data confirms sufficient public operational information.

A **Companies House-only** candidate is never treated as proof of a public Brighton trading
location. Registered-office and potentially residential information is suppressed unless an
independent operational source confirms it.

Event records require a source URL, usable title, valid date/time signal, locality/venue signal
and a primary/approved source or defined corroboration before public export.

See `docs/PUBLICATION-GATES.md`.

## Production thresholds

The Brighton profile contains release thresholds for directory depth, website/contact/geocode
coverage, multi-source coverage, future event count and source/venue coverage.

A weak run may still be useful for audit and review, but it must not silently replace the
last-known-good public feed.

## Website

`public_html/` is intentionally a Brighton consumer product, not a data-governance dashboard.
The website includes the map, What's On, travel, directory, community and business-listing
presentation.

Generated feeds are progressively enhanced into the existing pages. If a feed is absent or a
production release is held, the core site still renders safely.

## CI and operations

- `ci.yml` — tests, offline build and repository/site validation.
- `weekly-data.yml` — live source run, review/public artifacts, release gate.
- `production-readiness.yml` — strict release checks.
- `deploy-hostinger.yml` — manual upload of governed `public_html` using configured secrets.

## Lineage

The architecture is informed by the working patterns in:

- `sccnexusdata/leweslive`
- `sccnexusdata/LocalDirectory`
- `sccnexusdata/LocalEventsEngine`

Brighton-specific configuration lives here so the public product and its evidence pipeline can
be developed and released together without modifying the Lewes projects.
