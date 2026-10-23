<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Tracer / EPEVER

Read EPEVER and Tracer MPPT solar charge controllers over RS485 Modbus. Requires pymodbus 3.11 through 3.x and pyserial.

Package ID `tracer`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-tracer) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.3.0 |
| WeeWX | `>=5,<6` |
| Python | `>=3.10` |
| Release notes | [0.3.0](https://github.com/weewx-packages/weewx-tracer/releases/tag/v0.3.0) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-tracer/releases/download/v0.3.0/tracer-0.3.0.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install tracer --repo packages
python -m user.packages update tracer
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall tracer
```
