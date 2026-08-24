# Security

Do not report private credentials in public issues.

Secrets belong in GitHub Actions secrets or the hosting environment, never committed files.

If a credential, private address or other sensitive information is accidentally committed,
remove it from the active repository and rotate/revoke affected credentials. Treat Git history
as potentially retained and act accordingly.
