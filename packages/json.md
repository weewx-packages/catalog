<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# JSON reports

Render current and historical weather observations as JSON with optional sensor fields.

Package ID `json`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-json) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 1.3.0 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [1.3.0](https://github.com/weewx-packages/weewx-json/releases/tag/v1.3.0) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-json/releases/download/v1.3.0/weewx-json_1.3.0.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install)
installs by package ID and keeps track of updates. Register this catalog
as `packages` [once](../README.md#use-repository-search-and-updates), then run:

```shell
python -m user.packages install json --repo packages
python -m user.packages update JSON
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall JSON
```
