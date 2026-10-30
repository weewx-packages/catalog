<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Package manager

Install, search and update WeeWX extensions from repository indexes.

Package ID `package-manager`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-package-manager) lists its
further settings.

## Current release

| | |
|---|---|
| Version | 0.1.0a4 (prerelease) |
| WeeWX | `>=5,<6` |
| Python | `>=3.10` |
| Release notes | [0.1.0a4](https://github.com/weewx-packages/weewx-package-manager/releases/tag/v0.1.0a4) |

## Requirements

With WeeWX installed from its Debian or Raspberry Pi OS package:

```shell
sudo apt install python3-packaging
```

With a pip installation of WeeWX, activate its virtual environment first:

```shell
python -m pip install packaging
```

## Install with stock WeeWX

```shell
sudo weectl extension install https://github.com/weewx-packages/weewx-package-manager/releases/download/v0.1.0a4/package-manager-0.1.0a4.tar.gz
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
python -m user.packages install package-manager --repo packages --pre
python -m user.packages update package-manager --pre
```

The second command installs a later release when the catalog lists one.
Both check the requirements, install missing Python packages into a virtual
environment and print the setup steps. `python -m user.packages requirements package-manager`
checks them again later.

## Remove

```shell
weectl extension uninstall package-manager
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 0.1.0a3 | `>=5,<6` | `>=3.10` | [Download](https://github.com/weewx-packages/weewx-package-manager/releases/download/v0.1.0a3/package-manager-0.1.0a3.tar.gz) |
