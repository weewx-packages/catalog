<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Davis WeatherLink Cloud (pre-release)

Unified Davis cloud current conditions, archives and optional health service. Pre-release; legacy package migration is incomplete.

Package ID `davis-cloud`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-davis-cloud) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.1.0a2 (prerelease) |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |
| Release notes | [0.1.0a2](https://github.com/weewx-packages/weewx-davis-cloud/releases/tag/v0.1.0a2) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-davis-cloud/releases/download/v0.1.0a2/davis-cloud-0.1.0a2.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install davis-cloud --repo packages --pre
python -m user.packages update davis-cloud --pre
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall davis-cloud
```

## Other releases

| Version | WeeWX | Python | Archive |
|---|---|---|---|
| 0.1.0a1 | `>=5.5,<6` | `>=3.10,<3.15` | [Download](https://github.com/weewx-packages/weewx-davis-cloud/releases/download/v0.1.0a1/davis-cloud-0.1.0a1.tar.gz) |
