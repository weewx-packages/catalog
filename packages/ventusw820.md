<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Ventus W820

Read Ventus W820 weather observations over Bluetooth LE. Requires bluepy and a supported Bluetooth adapter.

Package ID `ventusw820`. The [installation and configuration guide](https://github.com/weewx-packages/ventusw820) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.2.2 |
| WeeWX | `>=5.2,<6` |
| Python | `>=3.10` |
| Release notes | [0.2.2](https://github.com/weewx-packages/ventusw820/releases/tag/v0.2.2) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/ventusw820/releases/download/v0.2.2/ventusw820-0.2.2.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install ventusw820 --repo packages
python -m user.packages update ventusw820
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall ventusw820
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 0.2.1 | `>=5.2,<6` | `>=3.10` | [Download](https://github.com/weewx-packages/ventusw820/releases/download/v0.2.1/ventusw820-0.2.1.zip) |
