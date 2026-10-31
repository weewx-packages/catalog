<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# pusher

Send realtime weather data to Pusher.

The author maintains this project at [raymondelooff/weewx-pusher](https://github.com/raymondelooff/weewx-pusher). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `pusher`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-pusher) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 2.0.1 |
| WeeWX | `>=5.5.2,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/pusher/v2.0.1/pusher-2.0.1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install pusher --repo packages
python -m user.packages update pusher
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall pusher
```
