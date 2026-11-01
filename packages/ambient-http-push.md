<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Ambient HTTP Push

Receive the custom server uploads of Ambient Weather consoles. Pre-release.

Package ID `ambient-http-push`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-ambient-http-push) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.1.0a1 (prerelease) |
| WeeWX | `>=5.5,<6` |
| Python | `>=3.10,<3.15` |
| Release notes | [0.1.0a1](https://github.com/weewx-packages/weewx-ambient-http-push/releases/tag/v0.1.0a1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-ambient-http-push/releases/download/v0.1.0a1/weewx-ambient-http-push-0.1.0a1.zip
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install ambient-http-push --repo packages --pre
python -m user.packages update ambient-http-push --pre
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall ambient-http-push
```
