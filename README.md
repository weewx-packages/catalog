# WeeWX packages

A shared catalog of WeeWX extensions, drivers, and skins. Register this catalog
once to search, install and update all packages it lists. Packages stay with
their publishers. This repository lists versioned downloads and the Python and
WeeWX versions each release supports.

## Add the catalog

These commands require a WeeWX build with extension repository support. They
are not available in an unmodified WeeWX 5.5.2 installation.

```shell
weectl extension repo add packages https://raw.githubusercontent.com/weewx-packages/catalog/main/repository.json
weectl extension search php
weectl extension install livedata
```

If another source publishes the same package ID, installation asks which source
to use. To select this catalog explicitly:

```shell
weectl extension install livedata --repo packages
```

Follow the package's configuration instructions after installation.

The mirrored skins use the same catalog. DivumWX requires Python 3.13.5 or later,
WeeWX 5.5 or later, and the `requests` and `skyfield` Python packages. Run your
station once to create its archive database before installing it. Its installer
asks for station settings and extends that database. Follow its upstream
uninstall instructions for the frontend and custom configuration it manages.
NeoWX Material may require selecting `skin = neowx-material` in your
`[[StandardReport]]` configuration and enabling that report.

<!-- packages:start -->
| Package | ID | Purpose |
|---|---|---|
| [LiveData](https://github.com/weewx-packages/weewx-livedata) | `livedata` | Publish live WeeWX readings as static JSON through a signed PHP endpoint. |
| [Ecowitt HTTP Push](https://github.com/weewx-packages/weewx-ecowitt-http-push) | `ecowitt-http-push` | Receive HTTP push uploads from Ecowitt gateways and consoles using the Ecowitt or Weather Underground custom-server protocol. |
| [Davis RTL-SDR](https://github.com/weewx-packages/weewx-rtldavis) | `rtldavis` | Receive Davis Vantage Pro, Pro2 and Vue wireless observations through RTL-SDR. Requires the separately built rtldavis receiver. |
<!-- packages:end -->

New packages become available through the same registered source when its index
refreshes. Use `weectl extension repo refresh packages` to refresh it explicitly.

## Check and update

```shell
weectl extension check-updates
weectl extension update
```

The selected source remains bound to the installed extension. Updates check its
compatibility and archive digest, and ask before replacing local changes.
Updates run when requested; this catalog sets up no background updater.

## Publish a package

See [CONTRIBUTING.md](CONTRIBUTING.md) for adding a package or release.
The published index is [repository.json](repository.json). Its structural
contract is [repository-v1.schema.json](schemas/repository-v1.schema.json).

Installing an extension executes its publisher's Python installer. An archive
digest checks agreement with the index, so use catalogs and publishers you trust.

## Compatibility checks

[GitHub Actions](https://github.com/weewx-packages/catalog/actions/workflows/compatibility.yml)
tests catalog releases daily against WeeWX `master` and `development`.
Failures open or update a [compatibility issue](https://github.com/weewx-packages/catalog/issues?q=label%3Acompatibility).
See [the checks and their coverage](COMPATIBILITY.md).

The [upstream skin workflow](https://github.com/weewx-packages/catalog/actions/workflows/upstreams.yml)
mirrors the three skin forks daily and publishes new stable versions after their
installation and report tests pass. The package table comes from the catalog
index and is updated in the same commit.

## License

The catalog, schema, and documentation use [GPL-3.0-only](LICENSE).
Listed packages retain their respective licenses.
