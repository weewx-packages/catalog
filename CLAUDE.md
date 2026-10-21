# WeeWX package catalog

Static JSON index for WeeWX clients with extension repository support.

## Validation

- `just fast`: validate the index with the client's semantic validator, about 0.1 s.
- Requires a WeeWX build with repository support and `weectl` on PATH.
- `just test-ci`: test CI planning, result handling and issue lifecycle.
  Requires pytest, packaging, Git and Bash.

## Structure

- `repository.json`: Published package index.
- `schemas/repository-v1.schema.json`: Version 1 structural contract.
- `CONTRIBUTING.md`: Package publication and validation procedure.
- `ci/packages.json`: Test source refs, installed imports and explicit skip reasons.
- `ci/compatibility.py`: Resolve commits, install release archives and run tests.
- `ci/issues.py`: Maintain compatibility issues from matrix artifacts.
- `ci/sync-weewx.sh`: Copy upstream branches and tags without executing source.
- `ci/upstreams.json`: Skin sources, release policy and test profiles.
- `ci/upstreams.py`: Select, package and publish tested upstream skin releases.
- `ci/skin_tests/`: Installed-skin report generation with an isolated archive.
- `COMPATIBILITY.md`: Check coverage, issue handling and adding package tests.

## Conventions

- Keep `repository.id` and existing package IDs stable.
- Use version-specific archive URLs and compute SHA-256 from downloaded bytes.
- Match installer names and versions to the actual archive.
- Keep published release bytes immutable; changes require a new version.
- Catalog entries do not change ownership or licensing of the listed projects.
- CI Python follows WeeWX's style, with types in Google docstrings.
- Keep extension execution separate from the job with issue-write permission.
- The mirror job alone receives `WEEWX_MIRROR_SSH_KEY`. Mirror updates must be
  atomic, preserve deleted upstream refs and reject divergent history.
- Skin mirror jobs receive only their own deploy key. Publishing credentials
  remain separate from upstream installers and report generators.
- Generate the README package table from repository.json; run
  `python3 ci/upstreams.py readme` after manual index changes.
