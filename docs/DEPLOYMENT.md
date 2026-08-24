# Deployment

## Public-site-only manual upload

The web root is `public_html/`. Its contents can be uploaded directly to the BrightonLive hosting
web root.

## GitHub Actions deployment

`deploy-hostinger.yml` is manual (`workflow_dispatch`) and:

1. installs/tests the repository;
2. runs the repository validator;
3. packages `public_html`;
4. uploads it to the configured Hostinger path.

It does **not** automatically run the live data harvest.

For a data refresh, first run `weekly-data.yml` or the live pipeline and inspect its release
report. Promote only when the release gate passes.

## Safe release sequence

```text
live harvest
→ internal/review/public artifacts
→ per-record validation
→ coverage/release gate
→ promote governed feeds
→ build public_html
→ deploy
→ smoke check
```

Do not let an adapter outage replace a healthy live feed with a tiny or empty one.
