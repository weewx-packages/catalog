<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# LiveData

Publish live WeeWX readings as static JSON through a signed PHP endpoint.

Package ID `livedata`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-livedata) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.2.0 |
| WeeWX | `>=5.2,<6` |
| Python | `>=3.7` |
| Release notes | [0.2.0](https://github.com/weewx-packages/weewx-livedata/releases/tag/v0.2.0) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-livedata/releases/download/v0.2.0/weewx-livedata-0.2.0.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install livedata --repo packages
python -m user.packages update livedata
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall livedata
```
