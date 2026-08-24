# Publication gates

## Directory

A directory record must first pass deterministic validation and have complete provenance.

It can then become `publication_ready` by an allowed route:

1. explicit human verification;
2. suitable authoritative Class A source;
3. organisation-owned operational structured data;
4. configured number of independent corroborating sources.

### Hard hold examples

- Companies House registered office with no operational-location corroboration;
- private/residential address that has not been explicitly approved for publication;
- malformed or missing identity/category;
- invalid coordinate or postcode;
- contradictory sources;
- insufficient corroboration.

## Events

A public event requires:

- non-placeholder title;
- valid start date/time;
- venue/postcode/coordinate signal;
- source URL;
- complete provenance;
- primary/official source, explicit manual verification or defined corroboration.

Raw discovery and search leads are not public events.

## Coverage gate

Per-record safety is necessary but not sufficient for replacing production feeds.

The release report separately checks:
- total directory count;
- category depth;
- website/contact/geocode coverage;
- multi-source coverage;
- event volume;
- event source/venue/geocode coverage.

If the release gate fails, retain the previous governed feed and upload the new run as
review/audit material only.
