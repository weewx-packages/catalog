<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Nova SDS011

Add SDS011 particulate concentrations through a serial sensor or a local Sensor.Community HTTP endpoint.

The author maintains this project at [weewx-contrib/weewx-NovaSDS011](https://github.com/weewx-contrib/weewx-NovaSDS011). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `nova-sds011`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-NovaSDS011/blob/weewx-packages-docs/README.md) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.1.0 |
| WeeWX | `>=5.2,<6` |
| Python | `>=3.10` |
| Release notes | [1.1.0](https://github.com/weewx-packages/weewx-NovaSDS011/releases/tag/v1.1.0) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-NovaSDS011/releases/download/v1.1.0/weewx-NovaSDS011-1.1.0.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install nova-sds011 --repo packages
python -m user.packages update NovaSDS011
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall NovaSDS011
```
