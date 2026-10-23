<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Zabbix sender service

Send WeeWX observations through zabbix_sender and provide a Zabbix 7 template for METRICWX inputs.

Package ID `zabbix`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-zabbix) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.2.0 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [0.2.0](https://github.com/weewx-packages/weewx-zabbix/releases/tag/v0.2.0) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-zabbix/releases/download/v0.2.0/weewx-zabbix-0.2.0.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install zabbix --repo packages
python -m user.packages update zabbix
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall zabbix
```
