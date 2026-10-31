<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-maxbotix

driver for maxbotix range-finding sensors

The author maintains this project at [matthewwall/weewx-maxbotix](https://github.com/matthewwall/weewx-maxbotix). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `maxbotix`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-maxbotix) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.9 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/maxbotix/v0.9/maxbotix-0.9.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install maxbotix --repo packages
python -m user.packages update maxbotix
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall maxbotix
```
