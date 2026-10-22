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

The mirrored skins use the same catalog. DivumWX 1.7.0.post1 replaces restricted
fonts with licensed fonts and Unicode symbols. The original 1.7.0 catalog
archive is withdrawn; future upstream tags require another font review.
NeoWX Material may require selecting `skin = neowx-material` in your
`[[StandardReport]]` configuration and enabling that report.

Tracer / EPEVER requires `pymodbus>=3.11,<4` and `pyserial`. Version 0.3.0 uses
watt-hours for energy observations; review older energy values before combining
records from different driver versions.

<!-- packages:start -->
| Package | ID | Purpose |
|---|---|---|
| [LiveData](https://github.com/weewx-packages/weewx-livedata) | `livedata` | Publish live WeeWX readings as static JSON through a signed PHP endpoint. |
| [Ecowitt HTTP Push](https://github.com/weewx-packages/weewx-ecowitt-http-push) | `ecowitt-http-push` | Receive HTTP push uploads from Ecowitt gateways and consoles using the Ecowitt or Weather Underground custom-server protocol. |
| [Davis RTL-SDR](https://github.com/weewx-packages/weewx-rtldavis) | `rtldavis` | Receive Davis Vantage Pro, Pro2 and Vue wireless observations through RTL-SDR. Requires the separately built rtldavis receiver. |
| [NeoWX Material](https://github.com/weewx-packages/neowx-material) | `neowx-material` | Material-style weather website with interactive charts and live observations. |
| [Belchertown](https://github.com/weewx-packages/weewx-belchertown) | `belchertown` | Weather website with live observations, interactive charts and forecasts. |
| [Tracer / EPEVER](https://github.com/weewx-packages/weewx-tracer) | `tracer` | Read EPEVER and Tracer MPPT solar charge controllers over RS485 Modbus. Requires pymodbus 3.11 through 3.x and pyserial. |
| [Cumulus realtime output](https://github.com/weewx-packages/weewx-crt) | `crt` | Write Cumulus realtime files, optional realmore data and gauge output from WeeWX observations. |
| [Cumulus wxnow output](https://github.com/weewx-packages/weewx-cwxn) | `cwxn` | Write wxnow.txt with APRS humidity and missing-value handling from WeeWX observations. |
| [Graphite uploader](https://github.com/weewx-packages/weewx-graphite) | `graphite` | Send WeeWX observations with their original timestamps to a Carbon TCP receiver. |
| [InfluxDB uploader](https://github.com/weewx-packages/weewx-influx) | `influx` | Upload WeeWX observations to InfluxDB 1 or 2 with verified TLS and bounded archive replay. |
| [Meteotemplate uploader](https://github.com/weewx-packages/weewx-meteotemplate) | `meteotemplate` | Send WeeWX observations and configured optional sensor fields to a Meteotemplate server. |
| [OpenWeatherMap uploader](https://github.com/weewx-packages/weewx-owm) | `owm` | Upload WeeWX measurements to the OpenWeatherMap station API over HTTPS. |
| [Prometheus Pushgateway uploader](https://github.com/weewx-packages/weewx-prompush) | `prompush` | Send WeeWX observations in Prometheus text format to a Pushgateway. |
| [Twitter uploader](https://github.com/weewx-packages/weewx-twitter) | `twitter` | Post formatted WeeWX observations through Twython at elapsed intervals or fixed local times. |
| [Zabbix sender service](https://github.com/weewx-packages/weewx-zabbix) | `zabbix` | Send WeeWX observations through zabbix_sender and provide a Zabbix 7 template for METRICWX inputs. |
| [DivumWX](https://github.com/weewx-packages/weewx-divumwx) | `divumwx` | Live weather dashboard with charts, forecasts and astronomy pages. Cleaned font package; requires requests and skyfield. |
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
tests catalog releases weekly against WeeWX `master` and `development`.
Failures open or update a [compatibility issue](https://github.com/weewx-packages/catalog/issues?q=label%3Acompatibility).
See [the checks and their coverage](COMPATIBILITY.md).

The [upstream skin workflow](https://github.com/weewx-packages/catalog/actions/workflows/upstreams.yml)
mirrors each skin fork weekly and publishes new stable versions after its
installation and report tests pass. The package table comes from the catalog
index and is updated in the same commit.

The [wiki review](WIKI-AUDIT.md) records licensing, maintenance and successor
decisions for the complete extension list. Additional source backups run weekly,
distributed across Monday through Friday. Source installation checks and
[upstream activity](https://github.com/weewx-packages/catalog/issues?q=%22Upstream+activity%22)
are reported separately from the tested catalog releases. See
[backup coverage](COMPATIBILITY.md#source-backups-and-upstream-activity).

## License

The catalog, schema, and documentation use [GPL-3.0-only](LICENSE).
Listed packages retain their respective licenses.
