<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-vedirect

Collect data from Victron VEDirect devices

Package ID `vedirect`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-vedirect/blob/weewx-packages-docs/README.md) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.2.post1 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/vedirect/v0.2.post1/vedirect-0.2.post1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install vedirect --repo packages
python -m user.packages update vedirect
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall vedirect
```
