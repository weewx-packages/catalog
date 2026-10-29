<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Archivecheck

Inspect SQLite archive alignment and export reviewed corrections with verified backups.

Package ID `archivecheck`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-archivecheck) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.1.1 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [0.1.1](https://github.com/weewx-packages/weewx-archivecheck/releases/tag/v0.1.1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-archivecheck/releases/download/v0.1.1/weewx-archivecheck-0.1.1.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install archivecheck --repo packages
python -m user.packages update archivecheck
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall archivecheck
```
