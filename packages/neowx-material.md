<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# NeoWX Material

Material-style weather website with interactive charts and live observations.

Package ID `neowx-material`. The [installation and configuration guide](https://github.com/weewx-packages/neowx-material/blob/weewx-packages-docs/README.md) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.73.4 |
| WeeWX | `>=5,<6` |
| Python | `>=3.10` |
| Release notes | [1.73.4](https://github.com/seehase/neowx-material/releases/tag/1.73.4) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/neowx-material/v1.73.4/neowx-material-1.73.4.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install neowx-material --repo packages
python -m user.packages update neowx-material
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall neowx-material
```
