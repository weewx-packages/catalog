<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# DivumWX

Live weather dashboard with charts, forecasts and astronomy pages. Requires requests and skyfield.

Package ID `divumwx`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-divumwx/blob/weewx-packages-docs/README.md) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.7.0 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.13.5` |
| Release notes | [1.7.0](https://github.com/Millardiang/weewx-divumwx/releases/tag/ver1.7.0) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/divumwx/v1.7.0/divumwx-1.7.0.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install divumwx --repo packages
python -m user.packages update divumwx
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall divumwx
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 1.7.0.post1 | `>=5.5,<6` | `>=3.13.5` | Withdrawn |
