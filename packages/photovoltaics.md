<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-photovoltaics

Service to retrieve data from PV system E3/DC

The author maintains this project at [roe-dl/weewx-photovoltaics](https://github.com/roe-dl/weewx-photovoltaics). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `photovoltaics`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-photovoltaics) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.8 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/photovoltaics/v0.8/photovoltaics-0.8.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install photovoltaics --repo packages
python -m user.packages update Photovoltaics
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall Photovoltaics
```
