<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-airlink-extended

Record air quality as provided by a Davis AirLink sensor.

Package ID `airlink-extended`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-airlink-extended) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.4 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/airlink-extended/v1.4/airlink-extended-1.4.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install airlink-extended --repo packages
python -m user.packages update airlink
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall airlink
```
