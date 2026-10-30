<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Davis RTL-SDR

Receive Davis Vantage Pro, Pro2 and Vue wireless observations through RTL-SDR. The receiver runs inside WeeWX and needs numpy and librtlsdr.

Package ID `rtldavis`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-rtldavis) lists its
further settings.

## Current release

| | |
|---|---|
| Version | 0.22.1 |
| WeeWX | `>=5,<6` |
| Python | `>=3.7` |
| Release notes | [0.22.1](https://github.com/weewx-packages/weewx-rtldavis/releases/tag/v0.22.1) |

## Requirements

With WeeWX installed from its Debian or Raspberry Pi OS package:

```shell
sudo apt install python3-numpy librtlsdr0
```

With a pip installation of WeeWX, activate its virtual environment first:

```shell
python -m pip install numpy
sudo apt install librtlsdr0
```

## Install with stock WeeWX

```shell
sudo weectl extension install https://github.com/weewx-packages/weewx-rtldavis/releases/download/v0.22.1/weewx-rtldavis-0.22.1.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.

## Set up

```shell
sudo weectl station reconfigure --driver=user.rtldavis    # asks for band, ISS channel and rain bucket
sudo usermod -aG plugdev weewx    # lets WeeWX open the dongle
sudo systemctl restart weewx
journalctl -u weewx -f    # plug in the dongle; shows the frequency search and the first frames
```

For a pip installation, run `weectl` from its virtual environment without
`sudo`, and use the account that runs WeeWX instead of `weewx`.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install rtldavis --repo packages
python -m user.packages update rtldavis
```

The second command installs a later release when the catalog lists one.
Both check the requirements, install missing Python packages into a virtual
environment and print the setup steps. `python -m user.packages requirements rtldavis`
checks them again later.

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
