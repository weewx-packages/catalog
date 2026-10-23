<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# WeatherLink Live

Poll the WeatherLink Live local HTTP API, including separate ISS and wind transmitters.

Package ID `wll`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-wll) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.2.2 |
| WeeWX | `>=5.2,<6` |
| Python | `>=3.10` |
| Release notes | [0.2.2](https://github.com/weewx-packages/weewx-wll/releases/tag/v0.2.2) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-wll/releases/download/v0.2.2/weewx-wll-0.2.2.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install wll --repo packages
python -m user.packages update wll
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall wll
```
