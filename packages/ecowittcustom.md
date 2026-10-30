<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Ecowitt custom

Receive uploads from Ecowitt consoles and gateways set to a customized server. The driver of ecowittcustom, without its skins.

Package ID `ecowittcustom`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-ecowittcustom) lists its
further settings.

## Current release

| | |
|---|---|
| Version | 0.2.0.post1 |
| WeeWX | `>=5,<6` |
| Python | `>=3.10` |
| Release notes | [0.2.0.post1](https://github.com/weewx-packages/weewx-ecowittcustom/releases/tag/v0.2.0.post1) |

## Install with stock WeeWX

```shell
sudo weectl extension install https://github.com/weewx-packages/weewx-ecowittcustom/releases/download/v0.2.0.post1/weewx-ecowittcustom-0.2.0.post1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.

## Set up

```shell
sudo weectl station reconfigure --driver=user.ecowittcustom    # selects the driver
sudo systemctl restart weewx
```

For a pip installation, run `weectl` from its virtual environment without
`sudo`, and use the account that runs WeeWX instead of `weewx`.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install ecowittcustom --repo packages
python -m user.packages update ecowittcustom
```

The second command installs a later release when the catalog lists one.
Both check the requirements, install missing Python packages into a virtual
environment and print the setup steps. `python -m user.packages requirements ecowittcustom`
checks them again later.

## Remove

```shell
weectl extension uninstall ecowittcustom
```
