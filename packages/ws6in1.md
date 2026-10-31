<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-ws6in1

Collect data from WS6in1 PC connected console

The author maintains this project at [BobAtchley/weewx-ws6in1](https://github.com/BobAtchley/weewx-ws6in1). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `ws6in1`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-ws6in1) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.03 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/ws6in1/v1.03/ws6in1-1.03.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install ws6in1 --repo packages
python -m user.packages update WS6in1
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall WS6in1
```
