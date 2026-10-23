<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# purple

Read PurpleAir measurements and calculate air quality indices.

Package ID `purple`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-purple) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 7.2.2 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/purple/v7.2.2/purple-7.2.2.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install purple --repo packages
python -m user.packages update purple
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall purple
```
