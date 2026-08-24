# Upload this repository to GitHub

The ZIP is repository-root structured.

## GitHub web upload

1. Create the empty BrightonLive repository.
2. Extract the supplied ZIP.
3. Open the `BrightonLive` folder.
4. Upload **its contents** to the repository root — do not upload a second nested
   `BrightonLive/BrightonLive/` directory.
5. Commit.
6. Add optional repository secrets from `docs/SECRETS.md`.
7. Run **BrightonLive CI** first.
8. Run **BrightonLive Weekly Data** manually only after CI passes.
9. Inspect its three artifacts: public build, review queue and internal audit.
10. Do not run the Hostinger deployment until the public build is the version you want online.

The initial production browser feeds are intentionally empty. Test fixtures live only under
`data/fixtures/` and are not shipped into `public_html/assets/data/`.
