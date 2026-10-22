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
| [Meteostick](https://github.com/weewx-packages/weewx-meteostick) | `meteostick` | Read Meteostick weather observations over a serial connection. |
| [SDR](https://github.com/weewx-packages/weewx-sdr) | `sdr` | Read weather sensors through rtl_433. Requires a separately installed rtl_433 executable. |
| [Nova SDS011](https://github.com/weewx-packages/weewx-NovaSDS011) | `nova-sds011` | Add SDS011 particulate concentrations through a serial sensor or a local Sensor.Community HTTP endpoint. |
| [Ventus W820](https://github.com/weewx-packages/ventusw820) | `ventusw820` | Read Ventus W820 weather observations over Bluetooth LE. Requires bluepy and a supported Bluetooth adapter. |
| [WH23xx](https://github.com/weewx-packages/weewx-wh23xx) | `wh23xx` | Read Fine Offset WH23xx weather stations over USB. |
| [Vaisala WXT5x0](https://github.com/weewx-packages/weewx-wxt5x0) | `wxt5x0` | Read Vaisala WXT5x0 observations over serial or a TCP serial server. |
| [WeatherLink Live](https://github.com/weewx-packages/weewx-wll) | `wll` | Poll the WeatherLink Live local HTTP API, including separate ISS and wind transmitters. |
| [ObserverIP](https://github.com/weewx-packages/weewx-observerip) | `observerip` | Read Ambient ObserverIP observations directly or through an intercepted upload file. |
| [Air quality indices](https://github.com/weewx-packages/weewx-aqi) | `aqi` | Calculate air quality indices with explicit historical and EPA 2024 standards. Backfill with PYTHONPATH=station/bin python -m user.aqi.backfill. |
| [Computer monitor](https://github.com/weewx-packages/weewx-cmon) | `cmon` | Archive CPU, memory, disk and network measurements from the local computer. |
| [CSV output](https://github.com/weewx-packages/weewx-csv) | `csv` | Write LOOP packets or archive records as CSV, with optional atomic snapshots and decimal precision. |
| [JSON reports](https://github.com/weewx-packages/weewx-json) | `json` | Render current and historical weather observations as JSON with optional sensor fields. |
| [BME280 data service](https://github.com/weewx-packages/bme280wx) | `bme280wx` | Add temperature, humidity and pressure readings from an I2C BME280 sensor to LOOP packets. |
| [Niculskin](https://github.com/weewx-packages/niculskin) | `niculskin` | Render translated weather reports, historical tables and weather graphs. |
| [weewx-airlink](https://github.com/weewx-packages/weewx-airlink) | `airlink` | Record air quality as provided by a Davis AirLink sensor. |
| [weewx-airlink-extended](https://github.com/weewx-packages/weewx-airlink-extended) | `airlink-extended` | Record air quality as provided by a Davis AirLink sensor. |
| [weewx-as3935](https://github.com/weewx-packages/weewx-as3935) | `as3935` | Capture lightning data from AS3935 hardware |
| [weewx-atmocom-udp](https://github.com/weewx-packages/weewx-atmocom-udp) | `atmocom-udp` | Capture data from Atmocom interceptor via UDP broadcast packets of Weather Underground updates |
| [weewx-cm1](https://github.com/weewx-packages/weewx-cm1) | `cm1` | Collect data from Dyacon weather station using CM1 |
| [weewx-columbia-ms](https://github.com/weewx-packages/weewx-columbia-ms) | `columbia-ms` | Capture weather data from a Columbia Weather Systems MicroServer |
| [weewx-davisconsoleapi](https://github.com/weewx-packages/weewx-davisconsoleapi) | `davisconsoleapi` | Install davisconsoleapi driver |
| [weewx-ecowittGateway](https://github.com/weewx-packages/weewx-ecowittGateway) | `ecowittgateway` | WeeWX driver/service for Ecowitt gateways and consoles (local HTTP API, or TCP API for the GW1000). |
| [weewx-envoy](https://github.com/weewx-packages/weewx-envoy) | `envoy` | Capture data from Enphase Envoy |
| [weewx-gill-metconnect](https://github.com/weewx-packages/weewx-gill-metconnect) | `gill-metconnect` | WeewX driver for Gill MetConnect Stations. |
| [weewx-id5001](https://github.com/weewx-packages/weewx-id5001) | `id5001` | Install id5001 driver |
| [weewx-interceptor](https://github.com/weewx-packages/weewx-interceptor) | `interceptor` | Capture weather data from HTTP requests |
| [weewx-ip100](https://github.com/weewx-packages/weewx-ip100) | `ip100` | Capture weather data from Rainwise IP-100 |
| [weewx-luxtronik](https://github.com/weewx-packages/weewx-luxtronik) | `luxtronik` | Augment station data with data from Luxtronik heatpump controller. |
| [weewx-maxbotix](https://github.com/weewx-packages/weewx-maxbotix) | `maxbotix` | driver for maxbotix range-finding sensors |
| [weewx-modbus-tcp](https://github.com/weewx-packages/weewx-modbus-tcp) | `modbus-tcp` | ModbusTcp driver for weewx. |
| [weewx-netatmo](https://github.com/weewx-packages/weewx-netatmo) | `netatmo` | Driver for netatmo weather stations. |
| [weewx-nmea-xdr](https://github.com/weewx-packages/weewx-nmea-xdr) | `nmea-xdr` | Augment WeeWX records with data NMEA0183 XDR sentences. |
| [weewx-owfs](https://github.com/weewx-packages/weewx-owfs) | `owfs` | driver for one-wire devices connected via owfs |
| [weewx-photovoltaics](https://github.com/weewx-packages/weewx-photovoltaics) | `photovoltaics` | Service to retrieve data from PV system E3/DC |
| [weewx-precipmeter](https://github.com/weewx-packages/weewx-precipmeter) | `precipmeter` | WeeWX-Service to fetch and process disdrometer data |
| [weewx-reservoir](https://github.com/weewx-packages/weewx-reservoir) | `reservoir` | Add USGS reservoir level and precipitation data to WeeWX archive records |
| [weewx-snmp](https://github.com/weewx-packages/weewx-snmp) | `snmp` | fetch data by SNMP |
| [weewx-tempest-ws](https://github.com/weewx-packages/weewx-tempest-ws) | `tempest-ws` | Weatherflow Tempest Websocket Driver installer |
| [weewx-tfrc](https://github.com/weewx-packages/weewx-tfrc) | `tfrc` | Capture data from tfrc |
| [weewx-ultimate-push](https://github.com/weewx-packages/weewx-ultimate-push) | `ultimate-push` | Collect data from weather hardware that uploads to a custom server: Ecowitt, Weather Underground, Ambient Weather, WeatherFlow, Acurite and LaCrosse. |
| [weewx-uradmon](https://github.com/weewx-packages/weewx-uradmon) | `uradmon` | A service that collects data and generatesa weewx report that displays the valuesreturned from a uradmonitor unithttps://www.uradmonitor.com |
| [weewx-vedirect](https://github.com/weewx-packages/weewx-vedirect) | `vedirect` | Collect data from Victron VEDirect devices |
| [weewx-wmr89](https://github.com/weewx-packages/weewx-wmr89) | `wmr89` | Driver for the Oregon Scientific WMR89 |
| [weewx-ws6in1](https://github.com/weewx-packages/weewx-ws6in1) | `ws6in1` | Collect data from WS6in1 PC connected console |
| [weewx-xtide](https://github.com/weewx-packages/weewx-xtide) | `xtide` | Fetch Tide Forecasts. |
| [DWD](https://github.com/weewx-packages/weewx-DWD) | `dwd` | Retrieve DWD observations, forecasts and warnings. Catalog snapshot with station-local commands. |
| [weewx-GTS](https://github.com/weewx-packages/weewx-GTS) | `gts` | Calculate growing degree sums, local solar day boundaries and pressure corrections. |
| [airQ](https://github.com/weewx-packages/weewx-airQ) | `airq` | Read air-Q environmental sensors through encrypted HTTP replies. Includes the user.airq_conf configuration tool. Prerelease. |
| [airgradient](https://github.com/weewx-packages/weewx-airgradient) | `airgradient` | Read AirGradient air quality sensors and calculate particulate AQI. |
| [amphibian](https://github.com/weewx-packages/weewx-amphibian) | `amphibian` | Display weather history and charts in the Amphibian skin. |
| [weewx-aqi-xtype](https://github.com/weewx-packages/weewx-aqi-xtype) | `aqi-xtype` | Calculate EPA air quality indices and NowCast through WeeWX XTypes. Prerelease. |
| [carbonsteel-series](https://github.com/weewx-packages/weewx-carbonsteel-series) | `carbonsteel-series` | Display weather gauges with CarbonSteelSeries and publish converted realtime observations. |
| [weewx-climate](https://github.com/weewx-packages/weewx-climate) | `climate` | Download and query historical ACIS climate statistics. |
| [Conditions](https://github.com/weewx-packages/weewx-conditions) | `conditions` | Generate JSON weather summaries, current observations and archive datasets. |
| [Ecowitt Console Emulator](https://github.com/weewx-packages/weewx-ecowitt_console_emulator) | `ecowitt-console-emulator` | Display an Ecowitt console dashboard and store its weather observations. |
| [exfoliation](https://github.com/weewx-packages/weewx-exfoliation) | `exfoliation` | Display weather reports with the Exfoliation skin. |
| [filepile](https://github.com/weewx-packages/weewx-filepile) | `filepile` | Merge named readings from a text file into archive records with unit conversion. |
| [forecasting](https://github.com/weewx-packages/weewx-forecast) | `forecast` | Generate Zambretti forecasts and retrieve forecast data from weather services. |
| [jas](https://github.com/weewx-packages/weewx-jas) | `jas` | Generate interactive weather charts and pages with the JAS skin. Prerelease. |
| [weewx-meteoalarm](https://github.com/weewx-packages/weewx-meteoalarm) | `meteoalarm` | Read CAP weather warning feeds and generate local warning reports. |
| [Metrics](https://github.com/weewx-packages/weewx-metrics) | `metrics` | Generate Prometheus metrics from WeeWX weather observations. |
| [MQTTSubscribe](https://github.com/weewx-packages/weewx-mqtt-subscribe) | `mqtt-subscribe` | Collect MQTT observations with field conversion, aggregation and expiring caches. Prerelease. |
| [weewx-nws](https://github.com/weewx-packages/weewx-nws) | `nws` | Retrieve NWS forecasts and warnings for local weather reports. |
| [OpenWeather API](https://github.com/weewx-packages/weewx-openweather_API) | `openweather-api` | Retrieve configured weather and air-quality fields from OpenWeather APIs. |
| [purple](https://github.com/weewx-packages/weewx-purple) | `purple` | Read PurpleAir measurements and calculate air quality indices. |
| [WeeWX-WD](https://github.com/weewx-packages/weewx-saratoga) | `saratoga` | Generate Saratoga weather data and calculate derived observations. |
| [sds011](https://github.com/weewx-packages/weewx-sds011) | `sds011` | Read particulate measurements from an SDS011 serial sensor. |
| [SetProcessName](https://github.com/weewx-packages/weewx-setprocessname) | `setprocessname` | Set the WeeWX daemon process title from configuration. |
| [Since Last Archive Accumulator](https://github.com/weewx-packages/weewx-since-last-archive-accumulator) | `since-last-archive-accumulator` | Accumulate rain and evapotranspiration between archive records. |
| [SQL](https://github.com/weewx-packages/weewx-sqlupload) | `sqlupload` | Split generated HTML and publish report data through SQL-backed PHP pages. |
| [SQM](https://github.com/weewx-packages/weewx-sqm) | `sqm` | Read SQM-LE TCP sky brightness measurements and calculate derived sky metrics. |
| [weewx-weatherboard](https://github.com/weewx-packages/weewx-weatherboard) | `weatherboard` | Display live weather observations with the WeatherBoard skin. |
| [weewx-xaggs](https://github.com/weewx-packages/weewx-xaggs) | `xaggs` | Calculate historical and threshold aggregations from daily weather summaries. |
| [WXgraphic](https://github.com/weewx-packages/weewx-WXgraphic) | `wxgraphic` | Weather Graphic image generator via a php script |
| [Aggregated Values](https://github.com/weewx-packages/weewx-aggregated-values) | `aggregated-values` | Calculate aggregated values that other extensions can then use without duplicating functionality and database lookups |
| [aprs](https://github.com/weewx-packages/weewx-aprs) | `aprs` | Write archive data in APRS positionless format. |
| [weewx-celestial](https://github.com/weewx-packages/weewx-celestial) | `celestial` | A live celestial report driven by weewx-loopdata almanac fields. |
| [weewx-easter-almanac-example](https://github.com/weewx-packages/weewx-easter-almanac-example) | `easter-almanac-example` | almanac extension example that calculates easter date |
| [emoncms](https://github.com/weewx-packages/weewx-emoncms) | `emoncms` | Upload weather data to EmonCMS. |
| [Healthchecks](https://github.com/weewx-packages/weewx-healthchecks) | `healthchecks` | Monitor WeeWX using Healthchecks.io. |
| [import-wlk](https://github.com/weewx-packages/weewx-import-wlk) | `import-wlk` | Pseudo-driver for importing WLK files |
| [knx](https://github.com/weewx-packages/weewx-knx) | `knx` | Write weather information to knx bus |
| [loopdata](https://github.com/weewx-packages/weewx-loopdata) | `loopdata` | Loop statistics for real time reporting. |
| [MQTTConfigHA](https://github.com/weewx-packages/weewx-mqtt-publish) | `mqtt-publish` | Publish WeeWX data to a MQTT broker. |
| [MQTTPublishV2](https://github.com/weewx-packages/weewx-mqtt-publish-v2) | `mqtt-publish-v2` | Publish WeeWX data to a MQTT broker. |
| [notifier](https://github.com/weewx-packages/weewx-notify) | `notify` | Notification to remote server Alternative installations: shares installer Notify and user/notify.py with Pushover; do not install together. |
| [grid voltage monitoring project uploader](https://github.com/weewx-packages/weewx-ortsnetz-auslastung) | `ortsnetz-auslastung` | upload grid voltages and frequency to the Ortsnetz-Auslastung project |
| [weewx-postgresql](https://github.com/weewx-packages/weewx-postgresql) | `postgresql` | WeeWX driver for the PostgreSQL database |
| [pusher](https://github.com/weewx-packages/weewx-pusher) | `pusher` | Send realtime weather data to Pusher. |
| [Pushover](https://github.com/weewx-packages/weewx-pushover) | `pushover` | Monitor observation values and send alerts. Alternative installations: shares installer Notify and user/notify.py with the webhook Notify extension; do not install together. |
| [RTSP Image](https://github.com/weewx-packages/weewx-rtsp-image) | `rtsp-image` | Capture still images from RTSP camera feeds using ffmpeg. |
| [Regionalwetter Sachsen-Anhalt](https://github.com/weewx-packages/weewx-rwsa) | `rwsa` | Upload weather data to Regionalwetter Sachsen-Anhalt. |
| [sftp (continuation fork)](https://github.com/weewx-packages/weewx-sftp) | `sftp` | Upload data using the sftp protocol |
| [weewx-skyfield](https://github.com/weewx-packages/weewx-skyfield) | `skyfield` | Replaces WeeWX's built-in almanac with a Skyfield based almanac for report generation. |
| [weewx-skyfield-almanac](https://github.com/weewx-packages/weewx-skyfield-almanac) | `skyfield-almanac` | almanac extension using Skyfield mdule |
| [weewx-skymap-almanac](https://github.com/weewx-packages/weewx-skymap-almanac) | `skymap-almanac` | almanac extension using Skyfield mdule |
| [Skyvex](https://github.com/weewx-packages/weewx-skyvex) | `skyvex` | Upload weather data to Skyvex (https://skyvex.org). |
| [weewx-svg2png](https://github.com/weewx-packages/weewx-svg2png) | `svg2png` | convert SVG to PNG files |
| [thingspeak](https://github.com/weewx-packages/weewx-thingspeak) | `thingspeak` | Upload weather data to ThingSpeak. |
| [weatherbug](https://github.com/weewx-packages/weewx-wbug) | `wbug` | Upload weather data to WeatherBug. |
| [weepe](https://github.com/weewx-packages/weewx-weepe) | `weepe` | Sends APRS formatted weather packets over a transport layer |
| [wetter](https://github.com/weewx-packages/weewx-wetter) | `wetter` | Upload weather data to wetter.com. |
| [windfinder](https://github.com/weewx-packages/weewx-windfinder) | `windfinder` | Upload weather data to WindFinder. |
| [windy](https://github.com/weewx-packages/weewx-windy) | `windy` | Upload weather data to Windy. |
| [wlip-emulator](https://github.com/weewx-packages/weewx-wlip-emulator) | `wlip-emulator` | WeatherLinkIP Emulator |
| [Wetternetz Sachsen](https://github.com/weewx-packages/weewx-wns) | `wns` | Upload weather data to WNS. |
| [wundergroundLike](https://github.com/weewx-packages/weewx-wundergroundlike) | `wundergroundlike` | Post to a custom server_url that uses Weather Underground formatting |
| [Davis WeatherLink Cloud (pre-release)](https://github.com/weewx-packages/weewx-davis-cloud) | `davis-cloud` | Unified Davis cloud current conditions, archives and optional health service. Pre-release; legacy package migration is incomplete. |
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
