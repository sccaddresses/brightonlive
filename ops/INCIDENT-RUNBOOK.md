# Incident runbook

## Symptoms
- empty calendar/directory;
- sudden record-count collapse;
- broken map cards;
- wrong location attached to a record;
- invalid/missing image;
- stale source output.

## Immediate action
1. Stop promotion/deployment.
2. Preserve the failing run under `exports/`.
3. Restore/retain `published/brighton/` last-known-good feeds.
4. Identify source-health or entity-resolution failure.
5. Re-run deterministic validation/tests.
6. Promote only after release gates recover.

Never solve a feed incident by weakening the publication gate.
