<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# WeatherLink Live

Poll the WeatherLink Live local HTTP API, including separate ISS and wind transmitters.

Package ID `wll`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-wll) lists its
further settings.

## Current release

| | |
|---|---|
| Version | 0.2.3 |
| WeeWX | `>=5.2,<6` |
| Python | `>=3.10` |
| Release notes | [0.2.3](https://github.com/weewx-packages/weewx-wll/releases/tag/v0.2.3) |

## Requirements

With WeeWX installed from its Debian or Raspberry Pi OS package:

```shell
sudo apt install python3-requests
```

With a pip installation of WeeWX, activate its virtual environment first:

```shell
python -m pip install 'requests>=2,<3'
```

## Install with stock WeeWX

```shell
sudo weectl extension install https://github.com/weewx-packages/weewx-wll/releases/download/v0.2.3/weewx-wll-0.2.3.zip
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
python -m user.packages install wll --repo packages
python -m user.packages update wll
```

The second command installs a later release when the catalog lists one.
Both check the requirements, install missing Python packages into a virtual
environment and print the setup steps. `python -m user.packages requirements wll`
checks them again later.

## Remove

```shell
weectl extension uninstall wll
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 0.2.2 | `>=5.2,<6` | `>=3.10` | [Download](https://github.com/weewx-packages/weewx-wll/releases/download/v0.2.2/weewx-wll-0.2.2.zip) |
