<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-stackedwindrose26

Stacked wind rose for WeeWX 5, drawn in the browser with D3.

The author maintains this project at [Millardiang/weewx-stackedwindrose26](https://github.com/Millardiang/weewx-stackedwindrose26). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `stackedwindrose26`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-stackedwindrose26) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.0.0 |
| WeeWX | `>=5.5.2,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/stackedwindrose26/v1.0.0/stackedwindrose26-1.0.0.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install stackedwindrose26 --repo packages
python -m user.packages update weewx-stackedwindrose26
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall weewx-stackedwindrose26
```
