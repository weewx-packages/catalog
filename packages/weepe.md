<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weepe

Sends APRS formatted weather packets over a transport layer

The author maintains this project at [w4kus/weewx-weepe](https://github.com/w4kus/weewx-weepe). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `weepe`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-weepe/blob/weewx-packages-docs/readme.md) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 2.0.2.post1 |
| WeeWX | `>=5.5.2,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/weepe/v2.0.2.post1/weepe-2.0.2.post1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install weepe --repo packages
python -m user.packages update weepe
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall weepe
```
