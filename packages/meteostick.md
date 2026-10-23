<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Meteostick

Read Meteostick weather observations over a serial connection.

Package ID `meteostick`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-meteostick) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.68.1 |
| WeeWX | `>=5.2,<6` |
| Python | `>=3.10` |
| Release notes | [0.68.1](https://github.com/weewx-packages/weewx-meteostick/releases/tag/v0.68.1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-meteostick/releases/download/v0.68.1/weewx-meteostick-0.68.1.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install meteostick --repo packages
python -m user.packages update meteostick
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall meteostick
```
