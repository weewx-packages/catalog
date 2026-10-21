# WeeWX package catalog

Static JSON index for WeeWX clients with extension repository support.

## Validation

- `just fast`: validate the index with the client's semantic validator, about 0.1 s.
- Requires a WeeWX build with repository support and `weectl` on PATH.

## Structure

- `repository.json`: Published package index.
- `schemas/repository-v1.schema.json`: Version 1 structural contract.
- `CONTRIBUTING.md`: Package publication and validation procedure.

## Conventions

- Keep `repository.id` and existing package IDs stable.
- Use version-specific archive URLs and compute SHA-256 from downloaded bytes.
- Match installer names and versions to the actual archive.
- Keep published release bytes immutable; changes require a new version.
- Catalog entries do not change ownership or licensing of the listed projects.
