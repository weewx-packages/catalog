<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-netatmo

Driver for netatmo weather stations.

Package ID `netatmo`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-netatmo) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.17 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/netatmo/v0.17/netatmo-0.17.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install netatmo --repo packages
python -m user.packages update netatmo
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall netatmo
```
