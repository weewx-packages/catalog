<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Vaisala WXT5x0

Read Vaisala WXT5x0 observations over serial or a TCP serial server.

Package ID `wxt5x0`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-wxt5x0) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.9.0 |
| WeeWX | `>=5.2,<6` |
| Python | `>=3.10` |
| Release notes | [0.9.0](https://github.com/weewx-packages/weewx-wxt5x0/releases/tag/v0.9.0) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-wxt5x0/releases/download/v0.9.0/weewx-wxt5x0-0.9.0.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install wxt5x0 --repo packages
python -m user.packages update wxt5x0
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall wxt5x0
```
