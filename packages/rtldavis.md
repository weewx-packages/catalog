<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Davis RTL-SDR

Receive Davis Vantage Pro, Pro2 and Vue wireless observations through RTL-SDR. The receiver runs inside WeeWX and needs numpy and librtlsdr.

Package ID `rtldavis`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-rtldavis) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.22.1 |
| WeeWX | `>=5,<6` |
| Python | `>=3.7` |
| Release notes | [0.22.1](https://github.com/weewx-packages/weewx-rtldavis/releases/tag/v0.22.1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-rtldavis/releases/download/v0.22.1/weewx-rtldavis-0.22.1.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install rtldavis --repo packages
python -m user.packages update rtldavis
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall rtldavis
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 0.22.0 | `>=5,<6` | `>=3.7` | [Download](https://github.com/weewx-packages/weewx-rtldavis/releases/download/v0.22.0/weewx-rtldavis-0.22.0.zip) |
| 0.21.2 | `>=5,<6` | `>=3.7` | [Download](https://github.com/weewx-packages/weewx-rtldavis/releases/download/v0.21.2/weewx-rtldavis-0.21.2.zip) |
| 0.21.1 | `>=5,<6` | `>=3.7` | [Download](https://github.com/weewx-packages/weewx-rtldavis/releases/download/v0.21.1/weewx-rtldavis-0.21.1.zip) |
