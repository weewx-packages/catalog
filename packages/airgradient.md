<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# airgradient

Read AirGradient air quality sensors and calculate particulate AQI.

Package ID `airgradient`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-airgradient) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 4.0 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/airgradient/v4.0/airgradient-4.0.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install airgradient --repo packages
python -m user.packages update airgradient
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall airgradient
```
