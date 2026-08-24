# Postcode-driven locality engine

BrightonLive is intentionally self-contained: it does not require the LewesLive,
LocalDirectory or LocalEventsEngine repositories at runtime.

The backend is nevertheless being kept **locality-driven rather than Brighton-hard-coded**.
The long-term reusable product should take a UK postcode (plus an optional radius and public
postcode districts) and generate the same contracts:

1. source discovery / harvesting;
2. provenance and integrity evidence;
3. entity resolution and event de-duplication;
4. locality and consumer-publication gates;
5. directory JSON + GeoJSON;
6. events JSON + GeoJSON;
7. map, directory and calendar feeds.

`src/brightonlive/locality.py` contains the first reusable locality boundary and postcode
resolver. `config/locality-template.yaml` documents the portable profile shape.

## Why not create another repository now?

One working Brighton repository is easier to operate and debug.  Once the Brighton workflow is
proven with real directory/event coverage, the generic modules can be extracted once into a
single postcode-driven engine rather than maintaining three competing harvesting repositories.

The target later is conceptually:

```text
postcode + radius
      ↓
reusable locality engine
      ↓
certified directory/events/map bundle
      ↓
local branded site or postcode-search interface
```

BrightonLive remains the first production implementation and should not depend on SCC Nexus
naming, tokens or cross-repository artifacts.
