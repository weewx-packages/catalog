<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# ObserverIP

Read Ambient ObserverIP observations directly or through an intercepted upload file.

Package ID `observerip`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-observerip) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.2.2 |
| WeeWX | `>=5.2,<6` |
| Python | `>=3.10` |
| Release notes | [0.2.2](https://github.com/weewx-packages/weewx-observerip/releases/tag/v0.2.2) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-observerip/releases/download/v0.2.2/weewx-observerip-0.2.2.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install observerip --repo packages
python -m user.packages update observerip
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall observerip
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 0.2.1.post20261022 | `>=5.2,<6` | `>=3.10` | [Download](https://github.com/weewx-packages/catalog/releases/download/observerip/v0.2.1.post20261022/observerip-0.2.1.post20261022.tar.gz) |
| 0.2.1 | `>=5.2,<6` | `>=3.10` | Withdrawn |
