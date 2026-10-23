<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Ecowitt HTTP Push

Receive HTTP push uploads from Ecowitt gateways and consoles using the Ecowitt or Weather Underground custom-server protocol.

Package ID `ecowitt-http-push`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-ecowitt-http-push) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.3.2 |
| WeeWX | `>=5,<6` |
| Python | `>=3.7` |
| Release notes | [0.3.2](https://github.com/weewx-packages/weewx-ecowitt-http-push/releases/tag/v0.3.2) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-ecowitt-http-push/releases/download/v0.3.2/weewx-ecowitt-http-push-0.3.2.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install ecowitt-http-push --repo packages
python -m user.packages update ecowitt
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall ecowitt
```
