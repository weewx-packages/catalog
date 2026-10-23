<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Prometheus Pushgateway uploader

Send WeeWX observations in Prometheus text format to a Pushgateway.

Package ID `prompush`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-prompush) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.1.1 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [1.1.1](https://github.com/weewx-packages/weewx-prompush/releases/tag/v1.1.1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-prompush/releases/download/v1.1.1/weewx-prompush-1.1.1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install prompush --repo packages
python -m user.packages update PromPush
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall PromPush
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 1.1.0 | `>=5.5.2,<5.7` | `>=3.10,<3.15` | [Download](https://github.com/weewx-packages/weewx-prompush/releases/download/v1.1.0/weewx-prompush-1.1.0.tar.gz) |
