# WeeWX packages

A shared catalog of WeeWX extensions, drivers, and skins. It lists versioned
downloads and the Python and WeeWX versions each release supports. Packages
stay with their publishers.

## Install with stock WeeWX

Open the package's page through its ID in the table below. The page names the
current release, its WeeWX and Python requirements, and the `weectl extension install`
command for its archive. Stock WeeWX installs extension archives by URL or local
filename. The package's guide, linked from the same page, lists dependencies
and configuration.

## Use repository search and updates

Repository support is currently provided by the experimental
[standalone package manager](https://github.com/weewx-packages/weewx-package-manager#install).
There is no core integration. Stock `weectl extension` does not accept catalog
package IDs or provide `repo`, `search`, `check-updates` or `update` actions.

Install the standalone manager using its instructions. It is a source-built
prerelease without a published release archive. After a WeeWX extension
installation, put your station's `bin` directory on `PYTHONPATH` and use the
same Python interpreter as WeeWX:

```shell
export PYTHONPATH=/path/to/station/bin
python -m user.packages repo add packages https://raw.githubusercontent.com/weewx-packages/catalog/main/repository.json
python -m user.packages search php
python -m user.packages install livedata --repo packages
```

The explicit `--repo` selects this source if another registered repository
publishes the same package ID. A Python-package installation of the manager
also provides `weectl-packages` with the same actions.

Follow the individual package's configuration instructions after installation.

NeoWX Material, Belchertown and DivumWX mirror the original upstream source,
including fonts and bundled license notices. Their catalog archives preserve
the upstream release files. DivumWX uses the original 1.7.0 package; the modified
1.7.0.post1 package is withdrawn from new installations.
NeoWX Material may require selecting `skin = neowx-material` in your
`[[StandardReport]]` configuration and enabling that report.

Tracer / EPEVER requires `pymodbus>=3.11,<4` and `pyserial`. Version 0.3.0 uses
watt-hours for energy observations; review older energy values before combining
records from different driver versions.

<!-- packages:start -->
### Skins

| Package | Install | Purpose |
|---|---|---|
| [amphibian](https://github.com/weewx-packages/weewx-amphibian) | [`amphibian`](packages/amphibian.md) | Display weather history and charts in the Amphibian skin. |
| [Belchertown](https://github.com/weewx-packages/weewx-belchertown/blob/weewx-packages-docs/README.md) | [`belchertown`](packages/belchertown.md) | Weather website with live observations, interactive charts and forecasts. |
| [carbonsteel-series](https://github.com/weewx-packages/weewx-carbonsteel-series) | [`carbonsteel-series`](packages/carbonsteel-series.md) | Display weather gauges with CarbonSteelSeries and publish converted realtime observations. |
| [DivumWX](https://github.com/weewx-packages/weewx-divumwx/blob/weewx-packages-docs/README.md) | [`divumwx`](packages/divumwx.md) | Live weather dashboard with charts, forecasts and astronomy pages. Requires requests and skyfield. |
| [Ecowitt Console Emulator](https://github.com/weewx-packages/weewx-ecowitt_console_emulator) | [`ecowitt-console-emulator`](packages/ecowitt-console-emulator.md) | Display an Ecowitt console dashboard and store its weather observations. |
| [exfoliation](https://github.com/weewx-packages/weewx-exfoliation) | [`exfoliation`](packages/exfoliation.md) | Display weather reports with the Exfoliation skin. |
| [jas](https://github.com/weewx-packages/weewx-jas/blob/weewx-packages-docs/README.md) | [`jas`](packages/jas.md) | Generate interactive weather charts and pages with the JAS skin. Prerelease. |
| [JSON reports](https://github.com/weewx-packages/weewx-json) | [`json`](packages/json.md) | Render current and historical weather observations as JSON with optional sensor fields. |
| [NeoWX Material](https://github.com/weewx-packages/neowx-material/blob/weewx-packages-docs/README.md) | [`neowx-material`](packages/neowx-material.md) | Material-style weather website with interactive charts and live observations. |
| [Niculskin](https://github.com/weewx-packages/niculskin) | [`niculskin`](packages/niculskin.md) | Render translated weather reports, historical tables and weather graphs. |
| [weewx-weatherboard](https://github.com/weewx-packages/weewx-weatherboard) | [`weatherboard`](packages/weatherboard.md) | Display live weather observations with the WeatherBoard skin. |
| [WXgraphic](https://github.com/weewx-packages/weewx-WXgraphic/blob/weewx-packages-docs/README.md) | [`wxgraphic`](packages/wxgraphic.md) | Weather Graphic image generator via a php script |

### Drivers and data sources

| Package | Install | Purpose |
|---|---|---|
| [airgradient](https://github.com/weewx-packages/weewx-airgradient) | [`airgradient`](packages/airgradient.md) | Read AirGradient air quality sensors and calculate particulate AQI. |
| [airQ](https://github.com/weewx-packages/weewx-airQ/blob/weewx-packages-docs/README.md) | [`airq`](packages/airq.md) | Read air-Q environmental sensors through encrypted HTTP replies. Includes the user.airq_conf configuration tool. Prerelease. |
| [BME280 data service](https://github.com/weewx-packages/bme280wx) | [`bme280wx`](packages/bme280wx.md) | Add temperature, humidity and pressure readings from an I2C BME280 sensor to LOOP packets. |
| [Computer monitor](https://github.com/weewx-packages/weewx-cmon) | [`cmon`](packages/cmon.md) | Archive CPU, memory, disk and network measurements from the local computer. |
| [Davis RTL-SDR](https://github.com/weewx-packages/weewx-rtldavis) | [`rtldavis`](packages/rtldavis.md) | Receive Davis Vantage Pro, Pro2 and Vue wireless observations through RTL-SDR. Requires the separately built rtldavis receiver. |
| [Davis WeatherLink Cloud (pre-release)](https://github.com/weewx-packages/weewx-davis-cloud) | [`davis-cloud`](packages/davis-cloud.md) | Unified Davis cloud current conditions, archives and optional health service. Pre-release; legacy package migration is incomplete. |
| [Ecowitt HTTP Push](https://github.com/weewx-packages/weewx-ecowitt-http-push) | [`ecowitt-http-push`](packages/ecowitt-http-push.md) | Receive HTTP push uploads from Ecowitt gateways and consoles using the Ecowitt or Weather Underground custom-server protocol. |
| [filepile](https://github.com/weewx-packages/weewx-filepile) | [`filepile`](packages/filepile.md) | Merge named readings from a text file into archive records with unit conversion. |
| [import-wlk](https://github.com/weewx-packages/weewx-import-wlk) | [`import-wlk`](packages/import-wlk.md) | Pseudo-driver for importing WLK files |
| [Meteostick](https://github.com/weewx-packages/weewx-meteostick) | [`meteostick`](packages/meteostick.md) | Read Meteostick weather observations over a serial connection. |
| [MQTTSubscribe](https://github.com/weewx-packages/weewx-mqtt-subscribe/blob/weewx-packages-docs/README.md) | [`mqtt-subscribe`](packages/mqtt-subscribe.md) | Collect MQTT observations with field conversion, aggregation and expiring caches. Prerelease. |
| [Nova SDS011](https://github.com/weewx-packages/weewx-NovaSDS011/blob/weewx-packages-docs/README.md) | [`nova-sds011`](packages/nova-sds011.md) | Add SDS011 particulate concentrations through a serial sensor or a local Sensor.Community HTTP endpoint. |
| [ObserverIP](https://github.com/weewx-packages/weewx-observerip) | [`observerip`](packages/observerip.md) | Read Ambient ObserverIP observations directly or through an intercepted upload file. |
| [OpenWeather API](https://github.com/weewx-packages/weewx-openweather_API/blob/weewx-packages-docs/README.md) | [`openweather-api`](packages/openweather-api.md) | Retrieve configured weather and air-quality fields from OpenWeather APIs. |
| [purple](https://github.com/weewx-packages/weewx-purple) | [`purple`](packages/purple.md) | Read PurpleAir measurements and calculate air quality indices. |
| [SDR](https://github.com/weewx-packages/weewx-sdr) | [`sdr`](packages/sdr.md) | Read weather sensors through rtl_433. Requires a separately installed rtl_433 executable. |
| [sds011](https://github.com/weewx-packages/weewx-sds011/blob/weewx-packages-docs/readme) | [`sds011`](packages/sds011.md) | Read particulate measurements from an SDS011 serial sensor. |
| [SQM](https://github.com/weewx-packages/weewx-sqm/blob/weewx-packages-docs/README.md) | [`sqm`](packages/sqm.md) | Read SQM-LE TCP sky brightness measurements and calculate derived sky metrics. |
| [Tracer / EPEVER](https://github.com/weewx-packages/weewx-tracer) | [`tracer`](packages/tracer.md) | Read EPEVER and Tracer MPPT solar charge controllers over RS485 Modbus. Requires pymodbus 3.11 through 3.x and pyserial. |
| [Vaisala WXT5x0](https://github.com/weewx-packages/weewx-wxt5x0) | [`wxt5x0`](packages/wxt5x0.md) | Read Vaisala WXT5x0 observations over serial or a TCP serial server. |
| [Ventus W820](https://github.com/weewx-packages/ventusw820) | [`ventusw820`](packages/ventusw820.md) | Read Ventus W820 weather observations over Bluetooth LE. Requires bluepy and a supported Bluetooth adapter. |
| [WeatherLink Live](https://github.com/weewx-packages/weewx-wll) | [`wll`](packages/wll.md) | Poll the WeatherLink Live local HTTP API, including separate ISS and wind transmitters. |
| [weewx-airlink](https://github.com/weewx-packages/weewx-airlink) | [`airlink`](packages/airlink.md) | Record air quality as provided by a Davis AirLink sensor. |
| [weewx-airlink-extended](https://github.com/weewx-packages/weewx-airlink-extended) | [`airlink-extended`](packages/airlink-extended.md) | Record air quality as provided by a Davis AirLink sensor. |
| [weewx-as3935](https://github.com/weewx-packages/weewx-as3935) | [`as3935`](packages/as3935.md) | Capture lightning data from AS3935 hardware |
| [weewx-atmocom-udp](https://github.com/weewx-packages/weewx-atmocom-udp/blob/weewx-packages-docs/README.md) | [`atmocom-udp`](packages/atmocom-udp.md) | Capture data from Atmocom interceptor via UDP broadcast packets of Weather Underground updates |
| [weewx-cm1](https://github.com/weewx-packages/weewx-cm1/blob/weewx-packages-docs/README.md) | [`cm1`](packages/cm1.md) | Collect data from Dyacon weather station using CM1 |
| [weewx-columbia-ms](https://github.com/weewx-packages/weewx-columbia-ms) | [`columbia-ms`](packages/columbia-ms.md) | Capture weather data from a Columbia Weather Systems MicroServer |
| [weewx-davisconsoleapi](https://github.com/weewx-packages/weewx-davisconsoleapi/blob/weewx-packages-docs/README.md) | [`davisconsoleapi`](packages/davisconsoleapi.md) | Install davisconsoleapi driver |
| [weewx-ecowittGateway](https://github.com/weewx-packages/weewx-ecowittGateway) | [`ecowittgateway`](packages/ecowittgateway.md) | WeeWX driver/service for Ecowitt gateways and consoles (local HTTP API, or TCP API for the GW1000). |
| [weewx-envoy](https://github.com/weewx-packages/weewx-envoy/blob/weewx-packages-docs/README.md) | [`envoy`](packages/envoy.md) | Capture data from Enphase Envoy |
| [weewx-gill-metconnect](https://github.com/weewx-packages/weewx-gill-metconnect) | [`gill-metconnect`](packages/gill-metconnect.md) | WeewX driver for Gill MetConnect Stations. |
| [weewx-id5001](https://github.com/weewx-packages/weewx-id5001/blob/weewx-packages-docs/README.md) | [`id5001`](packages/id5001.md) | Install id5001 driver |
| [weewx-interceptor](https://github.com/weewx-packages/weewx-interceptor/blob/weewx-packages-docs/README.md) | [`interceptor`](packages/interceptor.md) | Capture weather data from HTTP requests |
| [weewx-ip100](https://github.com/weewx-packages/weewx-ip100) | [`ip100`](packages/ip100.md) | Capture weather data from Rainwise IP-100 |
| [weewx-luxtronik](https://github.com/weewx-packages/weewx-luxtronik) | [`luxtronik`](packages/luxtronik.md) | Augment station data with data from Luxtronik heatpump controller. |
| [weewx-maxbotix](https://github.com/weewx-packages/weewx-maxbotix) | [`maxbotix`](packages/maxbotix.md) | driver for maxbotix range-finding sensors |
| [weewx-modbus-tcp](https://github.com/weewx-packages/weewx-modbus-tcp) | [`modbus-tcp`](packages/modbus-tcp.md) | ModbusTcp driver for weewx. |
| [weewx-netatmo](https://github.com/weewx-packages/weewx-netatmo) | [`netatmo`](packages/netatmo.md) | Driver for netatmo weather stations. |
| [weewx-nmea-xdr](https://github.com/weewx-packages/weewx-nmea-xdr/blob/weewx-packages-docs/README.md) | [`nmea-xdr`](packages/nmea-xdr.md) | Augment WeeWX records with data NMEA0183 XDR sentences. |
| [weewx-owfs](https://github.com/weewx-packages/weewx-owfs) | [`owfs`](packages/owfs.md) | driver for one-wire devices connected via owfs |
| [weewx-photovoltaics](https://github.com/weewx-packages/weewx-photovoltaics) | [`photovoltaics`](packages/photovoltaics.md) | Service to retrieve data from PV system E3/DC |
| [weewx-precipmeter](https://github.com/weewx-packages/weewx-precipmeter) | [`precipmeter`](packages/precipmeter.md) | WeeWX-Service to fetch and process disdrometer data |
| [weewx-reservoir](https://github.com/weewx-packages/weewx-reservoir) | [`reservoir`](packages/reservoir.md) | Add USGS reservoir level and precipitation data to WeeWX archive records |
| [weewx-snmp](https://github.com/weewx-packages/weewx-snmp/blob/weewx-packages-docs/README.md) | [`snmp`](packages/snmp.md) | fetch data by SNMP |
| [weewx-tempest-ws](https://github.com/weewx-packages/weewx-tempest-ws) | [`tempest-ws`](packages/tempest-ws.md) | Weatherflow Tempest Websocket Driver installer |
| [weewx-tfrc](https://github.com/weewx-packages/weewx-tfrc) | [`tfrc`](packages/tfrc.md) | Capture data from tfrc |
| [weewx-ultimate-push](https://github.com/weewx-packages/weewx-ultimate-push) | [`ultimate-push`](packages/ultimate-push.md) | Collect data from weather hardware that uploads to a custom server: Ecowitt, Weather Underground, Ambient Weather, WeatherFlow, Acurite and LaCrosse. |
| [weewx-uradmon](https://github.com/weewx-packages/weewx-uradmon) | [`uradmon`](packages/uradmon.md) | A service that collects data and generatesa weewx report that displays the valuesreturned from a uradmonitor unithttps://www.uradmonitor.com |
| [weewx-vedirect](https://github.com/weewx-packages/weewx-vedirect/blob/weewx-packages-docs/README.md) | [`vedirect`](packages/vedirect.md) | Collect data from Victron VEDirect devices |
| [weewx-wmr89](https://github.com/weewx-packages/weewx-wmr89) | [`wmr89`](packages/wmr89.md) | Driver for the Oregon Scientific WMR89 |
| [weewx-ws6in1](https://github.com/weewx-packages/weewx-ws6in1) | [`ws6in1`](packages/ws6in1.md) | Collect data from WS6in1 PC connected console |
| [WH23xx](https://github.com/weewx-packages/weewx-wh23xx) | [`wh23xx`](packages/wh23xx.md) | Read Fine Offset WH23xx weather stations over USB. |

### Uploaders

| Package | Install | Purpose |
|---|---|---|
| [emoncms](https://github.com/weewx-packages/weewx-emoncms/blob/weewx-packages-docs/README.md) | [`emoncms`](packages/emoncms.md) | Upload weather data to EmonCMS. |
| [Graphite uploader](https://github.com/weewx-packages/weewx-graphite) | [`graphite`](packages/graphite.md) | Send WeeWX observations with their original timestamps to a Carbon TCP receiver. |
| [grid voltage monitoring project uploader](https://github.com/weewx-packages/weewx-ortsnetz-auslastung/blob/weewx-packages-docs/README.md) | [`ortsnetz-auslastung`](packages/ortsnetz-auslastung.md) | upload grid voltages and frequency to the Ortsnetz-Auslastung project |
| [InfluxDB uploader](https://github.com/weewx-packages/weewx-influx) | [`influx`](packages/influx.md) | Upload WeeWX observations to InfluxDB 1 or 2 with verified TLS and bounded archive replay. |
| [LiveData](https://github.com/weewx-packages/weewx-livedata) | [`livedata`](packages/livedata.md) | Publish live WeeWX readings as static JSON through a signed PHP endpoint. |
| [Meteotemplate uploader](https://github.com/weewx-packages/weewx-meteotemplate) | [`meteotemplate`](packages/meteotemplate.md) | Send WeeWX observations and configured optional sensor fields to a Meteotemplate server. |
| [MQTTConfigHA](https://github.com/weewx-packages/weewx-mqtt-publish) | [`mqtt-publish`](packages/mqtt-publish.md) | Publish WeeWX data to a MQTT broker. |
| [MQTTPublishV2](https://github.com/weewx-packages/weewx-mqtt-publish-v2) | [`mqtt-publish-v2`](packages/mqtt-publish-v2.md) | Publish WeeWX data to a MQTT broker. |
| [OpenWeatherMap uploader](https://github.com/weewx-packages/weewx-owm) | [`owm`](packages/owm.md) | Upload WeeWX measurements to the OpenWeatherMap station API over HTTPS. |
| [Prometheus Pushgateway uploader](https://github.com/weewx-packages/weewx-prompush) | [`prompush`](packages/prompush.md) | Send WeeWX observations in Prometheus text format to a Pushgateway. |
| [pusher](https://github.com/weewx-packages/weewx-pusher) | [`pusher`](packages/pusher.md) | Send realtime weather data to Pusher. |
| [Regionalwetter Sachsen-Anhalt](https://github.com/weewx-packages/weewx-rwsa) | [`rwsa`](packages/rwsa.md) | Upload weather data to Regionalwetter Sachsen-Anhalt. |
| [sftp (continuation fork)](https://github.com/weewx-packages/weewx-sftp) | [`sftp`](packages/sftp.md) | Upload data using the sftp protocol |
| [Skyvex](https://github.com/weewx-packages/weewx-skyvex) | [`skyvex`](packages/skyvex.md) | Upload weather data to Skyvex (https://skyvex.org). |
| [SQL](https://github.com/weewx-packages/weewx-sqlupload) | [`sqlupload`](packages/sqlupload.md) | Split generated HTML and publish report data through SQL-backed PHP pages. |
| [thingspeak](https://github.com/weewx-packages/weewx-thingspeak/blob/weewx-packages-docs/README.md) | [`thingspeak`](packages/thingspeak.md) | Upload weather data to ThingSpeak. |
| [Twitter uploader](https://github.com/weewx-packages/weewx-twitter) | [`twitter`](packages/twitter.md) | Post formatted WeeWX observations through Twython at elapsed intervals or fixed local times. |
| [weatherbug](https://github.com/weewx-packages/weewx-wbug/blob/weewx-packages-docs/README.md) | [`wbug`](packages/wbug.md) | Upload weather data to WeatherBug. |
| [weepe](https://github.com/weewx-packages/weewx-weepe/blob/weewx-packages-docs/readme.md) | [`weepe`](packages/weepe.md) | Sends APRS formatted weather packets over a transport layer |
| [wetter](https://github.com/weewx-packages/weewx-wetter/blob/weewx-packages-docs/README.md) | [`wetter`](packages/wetter.md) | Upload weather data to wetter.com. |
| [Wetternetz Sachsen](https://github.com/weewx-packages/weewx-wns) | [`wns`](packages/wns.md) | Upload weather data to WNS. |
| [windfinder](https://github.com/weewx-packages/weewx-windfinder/blob/weewx-packages-docs/README.md) | [`windfinder`](packages/windfinder.md) | Upload weather data to WindFinder. |
| [windy](https://github.com/weewx-packages/weewx-windy/blob/weewx-packages-docs/README.md) | [`windy`](packages/windy.md) | Upload weather data to Windy. |
| [wundergroundLike](https://github.com/weewx-packages/weewx-wundergroundlike) | [`wundergroundlike`](packages/wundergroundlike.md) | Post to a custom server_url that uses Weather Underground formatting |
| [Zabbix sender service](https://github.com/weewx-packages/weewx-zabbix) | [`zabbix`](packages/zabbix.md) | Send WeeWX observations through zabbix_sender and provide a Zabbix 7 template for METRICWX inputs. |

### Forecasts and warnings

| Package | Install | Purpose |
|---|---|---|
| [DWD](https://github.com/weewx-packages/weewx-DWD/blob/weewx-packages-docs/README.md) | [`dwd`](packages/dwd.md) | Retrieve DWD observations, forecasts and warnings. Catalog snapshot with station-local commands. |
| [forecasting](https://github.com/weewx-packages/weewx-forecast) | [`forecast`](packages/forecast.md) | Generate Zambretti forecasts and retrieve forecast data from weather services. |
| [weewx-meteoalarm](https://github.com/weewx-packages/weewx-meteoalarm) | [`meteoalarm`](packages/meteoalarm.md) | Read CAP weather warning feeds and generate local warning reports. |
| [weewx-nws](https://github.com/weewx-packages/weewx-nws) | [`nws`](packages/nws.md) | Retrieve NWS forecasts and warnings for local weather reports. |
| [weewx-xtide](https://github.com/weewx-packages/weewx-xtide) | [`xtide`](packages/xtide.md) | Fetch Tide Forecasts. |

### Other

| Package | Install | Purpose |
|---|---|---|
| [Aggregated Values](https://github.com/weewx-packages/weewx-aggregated-values) | [`aggregated-values`](packages/aggregated-values.md) | Calculate aggregated values that other extensions can then use without duplicating functionality and database lookups |
| [Air quality indices](https://github.com/weewx-packages/weewx-aqi) | [`aqi`](packages/aqi.md) | Calculate air quality indices with explicit historical and EPA 2024 standards. Backfill with PYTHONPATH=station/bin python -m user.aqi.backfill. |
| [aprs](https://github.com/weewx-packages/weewx-aprs) | [`aprs`](packages/aprs.md) | Write archive data in APRS positionless format. |
| [Conditions](https://github.com/weewx-packages/weewx-conditions/blob/weewx-packages-docs/README.md) | [`conditions`](packages/conditions.md) | Generate JSON weather summaries, current observations and archive datasets. |
| [CSV output](https://github.com/weewx-packages/weewx-csv) | [`csv`](packages/csv.md) | Write LOOP packets or archive records as CSV, with optional atomic snapshots and decimal precision. |
| [Cumulus realtime output](https://github.com/weewx-packages/weewx-crt) | [`crt`](packages/crt.md) | Write Cumulus realtime files, optional realmore data and gauge output from WeeWX observations. |
| [Cumulus wxnow output](https://github.com/weewx-packages/weewx-cwxn) | [`cwxn`](packages/cwxn.md) | Write wxnow.txt with APRS humidity and missing-value handling from WeeWX observations. |
| [Healthchecks](https://github.com/weewx-packages/weewx-healthchecks) | [`healthchecks`](packages/healthchecks.md) | Monitor WeeWX using Healthchecks.io. |
| [knx](https://github.com/weewx-packages/weewx-knx) | [`knx`](packages/knx.md) | Write weather information to knx bus |
| [loopdata](https://github.com/weewx-packages/weewx-loopdata) | [`loopdata`](packages/loopdata.md) | Loop statistics for real time reporting. |
| [Metrics](https://github.com/weewx-packages/weewx-metrics/blob/weewx-packages-docs/README.md) | [`metrics`](packages/metrics.md) | Generate Prometheus metrics from WeeWX weather observations. |
| [notifier](https://github.com/weewx-packages/weewx-notify/blob/weewx-packages-docs/README.md) | [`notify`](packages/notify.md) | Notification to remote server Alternative installations: shares installer Notify and user/notify.py with Pushover; do not install together. |
| [Pushover](https://github.com/weewx-packages/weewx-pushover) | [`pushover`](packages/pushover.md) | Monitor observation values and send alerts. Alternative installations: shares installer Notify and user/notify.py with the webhook Notify extension; do not install together. |
| [RTSP Image](https://github.com/weewx-packages/weewx-rtsp-image) | [`rtsp-image`](packages/rtsp-image.md) | Capture still images from RTSP camera feeds using ffmpeg. |
| [SetProcessName](https://github.com/weewx-packages/weewx-setprocessname) | [`setprocessname`](packages/setprocessname.md) | Set the WeeWX daemon process title from configuration. |
| [Since Last Archive Accumulator](https://github.com/weewx-packages/weewx-since-last-archive-accumulator) | [`since-last-archive-accumulator`](packages/since-last-archive-accumulator.md) | Accumulate rain and evapotranspiration between archive records. |
| [weewx-aqi-xtype](https://github.com/weewx-packages/weewx-aqi-xtype) | [`aqi-xtype`](packages/aqi-xtype.md) | Calculate EPA air quality indices and NowCast through WeeWX XTypes. Prerelease. |
| [weewx-celestial](https://github.com/weewx-packages/weewx-celestial) | [`celestial`](packages/celestial.md) | A live celestial report driven by weewx-loopdata almanac fields. |
| [weewx-climate](https://github.com/weewx-packages/weewx-climate) | [`climate`](packages/climate.md) | Download and query historical ACIS climate statistics. |
| [weewx-easter-almanac-example](https://github.com/weewx-packages/weewx-easter-almanac-example/blob/weewx-packages-docs/README.md) | [`easter-almanac-example`](packages/easter-almanac-example.md) | almanac extension example that calculates easter date |
| [weewx-GTS](https://github.com/weewx-packages/weewx-GTS) | [`gts`](packages/gts.md) | Calculate growing degree sums, local solar day boundaries and pressure corrections. |
| [weewx-postgresql](https://github.com/weewx-packages/weewx-postgresql/blob/weewx-packages-docs/README.md) | [`postgresql`](packages/postgresql.md) | WeeWX driver for the PostgreSQL database |
| [weewx-skyfield](https://github.com/weewx-packages/weewx-skyfield) | [`skyfield`](packages/skyfield.md) | Replaces WeeWX's built-in almanac with a Skyfield based almanac for report generation. |
| [weewx-skyfield-almanac](https://github.com/weewx-packages/weewx-skyfield-almanac/blob/weewx-packages-docs/README.md) | [`skyfield-almanac`](packages/skyfield-almanac.md) | almanac extension using Skyfield mdule |
| [weewx-skymap-almanac](https://github.com/weewx-packages/weewx-skymap-almanac/blob/weewx-packages-docs/README.md) | [`skymap-almanac`](packages/skymap-almanac.md) | almanac extension using Skyfield mdule |
| [weewx-svg2png](https://github.com/weewx-packages/weewx-svg2png) | [`svg2png`](packages/svg2png.md) | convert SVG to PNG files |
| [WeeWX-WD](https://github.com/weewx-packages/weewx-saratoga) | [`saratoga`](packages/saratoga.md) | Generate Saratoga weather data and calculate derived observations. |
| [weewx-xaggs](https://github.com/weewx-packages/weewx-xaggs) | [`xaggs`](packages/xaggs.md) | Calculate historical and threshold aggregations from daily weather summaries. |
| [wlip-emulator](https://github.com/weewx-packages/weewx-wlip-emulator) | [`wlip-emulator`](packages/wlip-emulator.md) | WeatherLinkIP Emulator |
<!-- packages:end -->

With the standalone manager, new packages become available when the registered
index refreshes. Use `python -m user.packages repo refresh packages` to refresh it
explicitly in the environment configured above.

## Check and update

```shell
python -m user.packages check-updates
python -m user.packages update
```

These are standalone-manager commands. The selected source remains bound to the
installed extension. Updates check its
compatibility and archive digest, and ask before replacing local changes.
Updates run when requested; this catalog sets up no background updater.
For a stock WeeWX installation without the manager, follow the package's
documented archive upgrade procedure.

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
