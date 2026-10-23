<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# carbonsteel-series

Display weather gauges with CarbonSteelSeries and publish converted realtime observations.

Package ID `carbonsteel-series`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-carbonsteel-series) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.0.0 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/carbonsteel-series/v1.0.0/carbonsteel-series-1.0.0.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install carbonsteel-series --repo packages
python -m user.packages update CarbonSteelSeries
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall CarbonSteelSeries
```
