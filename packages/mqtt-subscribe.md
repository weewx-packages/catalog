<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# MQTTSubscribe

Collect MQTT observations with field conversion, aggregation and expiring caches. Prerelease.

Package ID `mqtt-subscribe`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-mqtt-subscribe/blob/weewx-packages-docs/README.md) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 3.2.1rc1.post20261022 (prerelease) |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/mqtt-subscribe/v3.2.1rc1.post20261022/mqtt-subscribe-3.2.1rc1.post20261022.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install mqtt-subscribe --repo packages --pre
python -m user.packages update MQTTSubscribe --pre
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall MQTTSubscribe
```
