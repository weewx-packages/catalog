<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# thingspeak

Upload weather data to ThingSpeak.

Package ID `thingspeak`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-thingspeak/blob/weewx-packages-docs/README.md) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.9.post1 |
| WeeWX | `>=5.5.2,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/thingspeak/v0.9.post1/thingspeak-0.9.post1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install thingspeak --repo packages
python -m user.packages update thingspeak
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall thingspeak
```
