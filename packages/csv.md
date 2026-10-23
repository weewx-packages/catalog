<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# CSV output

Write LOOP packets or archive records as CSV, with optional atomic snapshots and decimal precision.

Package ID `csv`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-csv) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.12.1 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [0.12.1](https://github.com/weewx-packages/weewx-csv/releases/tag/v0.12.1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-csv/releases/download/v0.12.1/weewx-csv-0.12.1.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install csv --repo packages
python -m user.packages update csv
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall csv
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 0.12.0 | `>=5.5.2,<5.7` | `>=3.10,<3.15` | [Download](https://github.com/weewx-packages/weewx-csv/releases/download/v0.12.0/weewx-csv-0.12.0.zip) |
