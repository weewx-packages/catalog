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

The first package is [LiveData](https://github.com/weewx-packages/weewx-livedata),
which publishes live readings through `live.php`. Follow its configuration
instructions after installation.

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

## License

The catalog, schema, and documentation use [GPL-3.0-only](LICENSE).
Listed packages retain their respective licenses.
