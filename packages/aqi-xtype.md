<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-aqi-xtype

Calculate EPA air quality indices and NowCast through WeeWX XTypes. Prerelease.

The author maintains this project at [weewx-extensions/aqi-xtype](https://github.com/weewx-extensions/aqi-xtype). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `aqi-xtype`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-aqi-xtype) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 2.1.0rc1 (prerelease) |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/aqi-xtype/v2.1.0rc1/aqi-xtype-2.1.0rc1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install aqi-xtype --repo packages --pre
python -m user.packages update AQITYPE --pre
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall AQITYPE
```
