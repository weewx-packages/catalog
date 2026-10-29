<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# SDR

Read weather sensors through rtl_433. Requires a separately installed rtl_433 executable.

Package ID `sdr`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-sdr) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.100.0 |
| WeeWX | `>=5.2,<6` |
| Python | `>=3.10` |
| Release notes | [0.100.0](https://github.com/weewx-packages/weewx-sdr/releases/tag/v0.100.0) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-sdr/releases/download/v0.100.0/weewx-sdr-0.100.0.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install sdr --repo packages
python -m user.packages update sdr
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall sdr
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 0.99.2 | `>=5.2,<6` | `>=3.10` | [Download](https://github.com/weewx-packages/weewx-sdr/releases/download/v0.99.2/weewx-sdr-0.99.2.zip) |
| 0.99.1 | `>=5.2,<6` | `>=3.10` | [Download](https://github.com/weewx-packages/weewx-sdr/releases/download/v0.99.1/weewx-sdr-0.99.1.zip) |
