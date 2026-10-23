<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# airQ

Read air-Q environmental sensors through encrypted HTTP replies. Includes the user.airq_conf configuration tool. Prerelease.

Package ID `airq`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-airQ/blob/weewx-packages-docs/README.md) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.9b3.post20261022 (prerelease) |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/airq/v0.9b3.post20261022/airq-0.9b3.post20261022.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install airq --repo packages --pre
python -m user.packages update airQ --pre
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall airQ
```
