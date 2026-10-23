<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-reservoir

Add USGS reservoir level and precipitation data to WeeWX archive records

Package ID `reservoir`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-reservoir) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.1.0 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/reservoir/v1.1.0/reservoir-1.1.0.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install reservoir --repo packages
python -m user.packages update reservoir
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall reservoir
```
