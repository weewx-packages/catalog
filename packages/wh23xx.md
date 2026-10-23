<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# WH23xx

Read Fine Offset WH23xx weather stations over USB.

Package ID `wh23xx`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-wh23xx) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.15.1 |
| WeeWX | `>=5.2,<6` |
| Python | `>=3.10` |
| Release notes | [0.15.1](https://github.com/weewx-packages/weewx-wh23xx/releases/tag/v0.15.1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-wh23xx/releases/download/v0.15.1/weewx-wh23xx-0.15.1.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install wh23xx --repo packages
python -m user.packages update wh23xx
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall wh23xx
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 0.15.0 | `>=5.2,<6` | `>=3.10` | [Download](https://github.com/weewx-packages/weewx-wh23xx/releases/download/v0.15.0/weewx-wh23xx-0.15.0.zip) |
