<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-display

Write the data of a wall display as JSON: live readings, extremes and totals, history, forecast, sun and moon.

Package ID `display`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-display) lists its
further settings.

## Current release

| | |
|---|---|
| Version | 0.1.1 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10` |
| Release notes | [0.1.1](https://github.com/weewx-packages/weewx-display/releases/tag/v0.1.1) |

## Requirements

With WeeWX installed from its Debian or Raspberry Pi OS package:

```shell
sudo apt install python3-ephem
```

With a pip installation of WeeWX, activate its virtual environment first:

```shell
python -m pip install ephem
```

## Install with stock WeeWX

```shell
sudo weectl extension install https://github.com/weewx-packages/weewx-display/releases/download/v0.1.1/weewx-display-0.1.1.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Then restart WeeWX.

For a pip installation, run `weectl` from its virtual environment without
`sudo`, and use the account that runs WeeWX instead of `weewx`.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install display --repo packages
python -m user.packages update display
```

The second command installs a later release when the catalog lists one.
Both check the requirements, install missing Python packages into a virtual
environment and print the setup steps. `python -m user.packages requirements display`
checks them again later.

## Remove

```shell
weectl extension uninstall display
```
