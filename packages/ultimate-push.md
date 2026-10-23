<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-ultimate-push

Collect data from weather hardware that uploads to a custom server: Ecowitt, Weather Underground, Ambient Weather, WeatherFlow, Acurite and LaCrosse.

Package ID `ultimate-push`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-ultimate-push) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.21.0 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/ultimate-push/v0.21.0/ultimate-push-0.21.0.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install ultimate-push --repo packages
python -m user.packages update ultimate-push
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall ultimate-push
```
