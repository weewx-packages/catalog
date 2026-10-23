<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Air quality indices

Calculate air quality indices with explicit historical and EPA 2024 standards. Backfill with PYTHONPATH=station/bin python -m user.aqi.backfill.

Package ID `aqi`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-aqi) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.5.0.post20261022 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [1.5.0.post20261022](https://github.com/weewx-packages/weewx-aqi/releases/tag/v1.5.0) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/aqi/v1.5.0.post20261022/aqi-1.5.0.post20261022.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install aqi --repo packages
python -m user.packages update aqi
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall aqi
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 1.5.0 | `>=5.5.2,<5.7` | `>=3.10,<3.15` | Withdrawn |
