<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# amphibian

Display weather history and charts in the Amphibian skin.

The author maintains this project at [matthewwall/weewx-amphibian](https://github.com/matthewwall/weewx-amphibian). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `amphibian`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-amphibian) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.12 |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/amphibian/v0.12/amphibian-0.12.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install amphibian --repo packages
python -m user.packages update amphibian
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall amphibian
```
