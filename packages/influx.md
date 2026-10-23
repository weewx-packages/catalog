<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# InfluxDB uploader

Upload WeeWX observations to InfluxDB 1 or 2 with verified TLS and bounded archive replay.

Package ID `influx`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-influx) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.21.1 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [0.21.1](https://github.com/weewx-packages/weewx-influx/releases/tag/v0.21.1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-influx/releases/download/v0.21.1/weewx-influx-0.21.1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install influx --repo packages
python -m user.packages update influx
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall influx
```
