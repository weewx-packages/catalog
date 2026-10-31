<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-airlink

Record air quality as provided by a Davis AirLink sensor.

The author maintains this project at [chaunceygardiner/weewx-airlink](https://github.com/chaunceygardiner/weewx-airlink). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `airlink`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-airlink) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 4.1.1 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/airlink/v4.1.1/airlink-4.1.1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install airlink --repo packages
python -m user.packages update airlink
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall airlink
```
