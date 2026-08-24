# Brighton source registry

The initial event supplier configuration includes first-party/public sources for:

- VisitBrighton events calendar
- Brighton Dome
- Brighton Centre
- Komedia Brighton
- The Old Market
- Theatre Royal Brighton
- Brighton Fringe
- Brighton Festival
- Brighton & Hove City Council

The repository does not treat being present in this registry as equivalent to a publishable
event. The configured page must still yield an event record with provenance, date and
location/venue signal and pass the event verification rule.

As of the initial BrightonLive build on **23 August 2026**, current event content was confirmed
on VisitBrighton, Brighton Dome, Brighton Centre, Komedia and The Old Market during source
review. All configured sources are re-probed by the scheduled source-health workflow and can be
held or disabled without weakening the public event gate.

Directory discovery starts with FHRS, OpenStreetMap, optional Companies House, organisation-owned
JSON-LD and reviewed/manual data. CQC and Charity Commission contracts are represented but
disabled until their current downloadable-data handoff is implemented and tested in this
monorepo.
