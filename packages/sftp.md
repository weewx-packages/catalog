<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# sftp (continuation fork)

Upload data using the sftp protocol

Package ID `sftp`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-sftp) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.9.0 |
| WeeWX | `>=5.5.2,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/sftp/v0.9.0/sftp-0.9.0.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install sftp --repo packages
python -m user.packages update sftp
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall sftp
```
