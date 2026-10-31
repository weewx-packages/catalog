<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Pushover

Monitor observation values and send alerts. Alternative installations: shares installer Notify and user/notify.py with the webhook Notify extension; do not install together.

The author maintains this project at [weewx-extensions/pushover](https://github.com/weewx-extensions/pushover). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `pushover`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-pushover) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.3.0 |
| WeeWX | `>=5.5.2,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/pushover/v0.3.0/pushover-0.3.0.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install pushover --repo packages
python -m user.packages update Notify
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall Notify
```
