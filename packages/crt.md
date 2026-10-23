<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Cumulus realtime output

Write Cumulus realtime files, optional realmore data and gauge output from WeeWX observations.

Package ID `crt`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-crt) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.24.1 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [0.24.1](https://github.com/weewx-packages/weewx-crt/releases/tag/v0.24.1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-crt/releases/download/v0.24.1/weewx-crt-0.24.1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install crt --repo packages
python -m user.packages update crt
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall crt
```
