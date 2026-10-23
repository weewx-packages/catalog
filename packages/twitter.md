<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# Twitter uploader

Post formatted WeeWX observations through Twython at elapsed intervals or fixed local times.

Package ID `twitter`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-twitter) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.16.1 |
| WeeWX | `>=5.5.2,<5.7` |
| Python | `>=3.10,<3.15` |
| Release notes | [0.16.1](https://github.com/weewx-packages/weewx-twitter/releases/tag/v0.16.1) |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/weewx-twitter/releases/download/v0.16.1/weewx-twitter-0.16.1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install twitter --repo packages
python -m user.packages update twitter
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall twitter
```
