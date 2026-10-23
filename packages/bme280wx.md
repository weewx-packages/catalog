<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# BME280 data service

Add temperature, humidity and pressure readings from an I2C BME280 sensor to LOOP packets.

Package ID `bme280wx`. The [installation and configuration guide](https://github.com/weewx-packages/bme280wx) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.1.1 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [1.1.1](https://github.com/weewx-packages/bme280wx/releases/tag/v1.1.1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/bme280wx/releases/download/v1.1.1/bme280wx-1.1.1.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install bme280wx --repo packages
python -m user.packages update bme280wx
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall bme280wx
```
