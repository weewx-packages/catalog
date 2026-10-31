<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# jas

Generate interactive weather charts and pages with the JAS skin. Prerelease.

The author maintains this project at [weewx-extensions/jas](https://github.com/weewx-extensions/jas). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `jas`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-jas/blob/weewx-packages-docs/README.md) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.2.0rc3.post20261022 (prerelease) |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/jas/v1.2.0rc3.post20261022/jas-1.2.0rc3.post20261022.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install jas --repo packages --pre
python -m user.packages update jas --pre
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall jas
```
