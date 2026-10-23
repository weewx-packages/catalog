# WeeWX package catalog

Static JSON index for WeeWX clients with extension repository support.

## Validation

- `just fast`: validate the index with the client's semantic validator, about 0.1 s.
- Requires the standalone `user.packages` client importable by `python3`, using
  a Python-package install or the extension's station bin directory on PYTHONPATH.
- Stock WeeWX has no `weectl extension repo` command.
- `just test-ci`: test CI planning, result handling and issue lifecycle.
  Requires pytest, packaging, Git and Bash.

## Structure

- `repository.json`: Published package index.
- `schemas/repository-v1.schema.json`: Version 1 structural contract.
- `CONTRIBUTING.md`: Package publication and validation procedure.
- `ci/packages.json`: Test source refs, installed imports and explicit skip reasons.
- `ci/external.json`: Non-catalog projects and explicitly limited component checks.
- `ci/project_tests/`: Functional suites against verified payloads and installed stations.
- `ci/project_coverage.py`: Require a declared check for every tracked repository.
- `ci/compatibility.py`: Resolve commits, install release archives and run tests.
- `ci/installed_files.py`: Compare installed Python with the verified release payload.
- `ci/issues.py`: Maintain compatibility issues from matrix artifacts.
- `ci/sync-weewx.sh`: Copy upstream branches and tags without executing source.
- `ci/upstreams.json`: Skin sources, release policy and test profiles.
- `ci/upstreams.py`: Select, package and publish tested upstream skin releases.
- `ci/skin_tests/`: Installed-skin report generation with an isolated archive.
- `COMPATIBILITY.md`: Check coverage, issue handling and adding package tests.
- `WIKI-AUDIT.md`, `ci/wiki-audit.json`: Complete wiki review and pinned license evidence.
- `ci/mirrors.json`, `ci/mirrors.py`: Weekly source-backup groups and deploy-key handling.
- `ci/upstream_status.py`: Private discussion snapshots and public change summaries.
- `ci/wiki_backup.py`: Private wiki Git bundles with independent restore checks.
- `ci/wiki-state.json`: Public wiki availability and last verified backup status.
- `ci/source_quality.py`: Source installation checks, separate from release regression tests.

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
- Keep independent continuations at `sync: false`; their fixes must never be
  replaced by a routine upstream copy.
- Source, discussion backup, test and reporting jobs have separate credentials.
  Discussion bodies and PR patches belong in the private backup, not public artifacts.
