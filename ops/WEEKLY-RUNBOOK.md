# Weekly runbook

1. Run source probes.
2. Run the live pipeline.
3. Inspect `source-health.json`.
4. Inspect directory and event review queues.
5. Run release report.
6. If the release gate fails, **do not replace** last-known-good production feeds.
7. Resolve critical source or parsing failures.
8. Promote governed feeds.
9. Validate `public_html`.
10. Deploy.
11. Smoke-check Home, Map, What's On, Directory and a sample source link.
