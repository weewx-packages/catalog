<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->

# weewx-easter-almanac-example

almanac extension example that calculates easter date

The author maintains this project at [roe-dl/weewx-easter-almanac-example](https://github.com/roe-dl/weewx-easter-almanac-example). Ask for support and report
bugs there. The catalog keeps a backup copy, tests the releases and packages
them. Report problems with the catalog archive in the
[catalog issues](https://github.com/weewx-packages/catalog/issues).

Package ID `easter-almanac-example`. The [installation and configuration guide](https://github.com/weewx-packages/weewx-easter-almanac-example/blob/weewx-packages-docs/README.md) lists its
dependencies and settings.

## Current release

| | |
|---|---|
| Version | 0.1.post1 |
| WeeWX | `>=5.5.2,<6` |
| Python | `>=3.10,<3.15` |

## Install with stock WeeWX

Install the dependencies named in the guide first. Then use the `weectl`
of the Python environment running WeeWX:

```shell
weectl extension install https://github.com/weewx-packages/catalog/releases/download/easter-almanac-example/v0.1.post1/easter-almanac-example-0.1.post1.tar.gz
```

Add `--config /path/to/weewx.conf` if your station uses another configuration file.
Complete the configuration described in the guide. Then restart WeeWX.

## Install with the package manager

The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)
extension installs by package ID and keeps track of updates. Register this
catalog as `packages` once, as its documentation shows, then run:

```shell
python -m user.packages install easter-almanac-example --repo packages
python -m user.packages update EasterExample
```

The second command installs a later release when the catalog lists one.

## Remove

```shell
weectl extension uninstall EasterExample
```
