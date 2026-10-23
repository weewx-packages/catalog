<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Graphite uploader

Send WeeWX observations with their original timestamps to a Carbon TCP receiver.

Package ID `graphite`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-graphite) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 2.2.0 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [2.2.0](https://github.com/weewx-packages/weewx-graphite/releases/tag/v2.2.0) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-graphite/releases/download/v2.2.0/weewx-graphite-2.2.0.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install graphite --repo packages
python -m user.packages update graphite
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall graphite
```
