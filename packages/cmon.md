<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Computer monitor

Archive CPU, memory, disk and network measurements from the local computer.

Package ID `cmon`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-cmon) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.21.1 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [0.21.1](https://github.com/weewx-packages/weewx-cmon/releases/tag/v0.21.1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-cmon/releases/download/v0.21.1/weewx-cmon-0.21.1.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install cmon --repo packages
python -m user.packages update cmon
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall cmon
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 0.21.0 | `>=5.5.2,<5.7` | `>=3.10,<3.15` | [Download](https://github.com/weewx-packages/weewx-cmon/releases/download/v0.21.0/weewx-cmon-0.21.0.zip) |
