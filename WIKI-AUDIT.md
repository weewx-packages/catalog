# WeeWX wiki review

Review of the [WeeWX extension list](https://github.com/weewx/weewx/wiki),
snapshot `753c05f167aa8cc2cdde41543bca6eabdbe3f338`, on 22 October 2026.
All 203 extension entries were reviewed, plus SQLBackup and the related
WordPress plugin. Independent repairs and release checks are complete; rights,
hardware and seven unauthenticated GitLab replies remain documented follow-ups.

Source licenses and component notices were checked separately from GitHub
license labels. An old commit alone does not establish abandonment. Open
items created before 22 October 2025 were examined alongside maintainer
responses, recent commits and documented successors. Existing successors
take precedence over older variants.

A mirrored repository is a source backup. Installation and compatibility
coverage is recorded separately; presence here does not make it a tested
catalog package. Restricted use terms are recorded individually, rather
than treated as an automatic redistribution prohibition.

DivumWX uses the unchanged upstream 1.7.0 release, including its original fonts
and notices. The modified 1.7.0.post1 package is withdrawn from new installations.
Tracer 0.3.0 is published
with regression tests; physical controller validation remains outstanding.

The [machine-readable review](ci/wiki-audit.json) contains pinned license
evidence, tracker details, reasons, successor decisions and repair results.

| Wiki line | Project | License | Decision | Organization copy |
|---|---|---|---|---|
| 63 | [SQLBackup](https://github.com/glennmckechnie/weewx-sqlbackup) | GPL-3.0 | blocked_license_assets |  |
| 114 | [airmar](https://github.com/fullergalway/weewx-airmar-150wx-driver) | NOASSERTION | blocked_license |  |
| 115 | [ambientweatherapi-json](https://github.com/themoosman/weewx-ambientweatherapi-json) | LicenseRef-Partial-GPL-3.0 | blocked_license |  |
| 116 | [atmocom](https://github.com/captain-coredump/weewx-atmocom-udp) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-atmocom-udp) |
| 117 | [aws](https://github.com/wrybread/weewx-ArduinoWeatherStation) | GPL-3.0-only (installer only); LicenseRef-Unproven-Arduino-and-assets | blocked_distribution_rights |  |
| 118 | [BCRobotics](https://github.com/David-Enst/WeeWX-BCRobotics) | LicenseRef-Partial-GPL-3.0 | blocked_license |  |
| 119 | [byows_rpi](https://github.com/jardiamj/BYOWS_RPi) | GPL-3.0-or-later | hold_maintenance_borderline |  |
| 120 | [cm1](https://github.com/matthewwall/weewx-cm1) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-cm1) |
| 121 | [columbia_ms](https://github.com/bburton/weewx-columbia-ms) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-columbia-ms) |
| 122 | [envoy](https://github.com/matthewwall/weewx-envoy) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-envoy) |
| 123 | [Gill MetConnect](https://github.com/Cosmospacedog/Gill-WeeWX) | MIT | fork_created | [repository](https://github.com/weewx-packages/weewx-gill-metconnect) |
| 124 | [hackulink](https://geekfun.com/hackulink) | GPL-3.0-only | defer_external_import |  |
| 125 | [Hp1000](https://github.com/AussieSusan/HP1000) | NOASSERTION | blocked_license |  |
| 126 | [id5001](https://github.com/n2ee/weewx-id5001) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-id5001) |
| 127 | [interceptor](https://github.com/tfilo/weewx-interceptor) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-interceptor) |
| 128 | [ip100](https://github.com/chaunceygardiner/weewx-ip100) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-ip100) |
| 129 | [ipwx](http://nincehelser.com/ipwx) | NOASSERTION | blocked_source_unavailable |  |
| 130 | [klimalogg](https://github.com/matthewwall/weewx-klimalogg) | GPL-3.0-or-later (driver) | local_driver_fixes_distribution_blocked |  |
| 131 | [mate](https://github.com/matthewwall/weewx-mate) | NOASSERTION | blocked_license |  |
| 132 | [maxbotix](https://github.com/matthewwall/weewx-maxbotix) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-maxbotix) |
| 133 | [meteostick](https://github.com/matthewwall/weewx-meteostick) | GPL-3.0-or-later AND GPL-3.0-only | released | [repository](https://github.com/weewx-packages/weewx-meteostick) |
| 134 | [ModbusTCP](https://github.com/FColinet/WeeWX-ModbusTCP-driver) | MIT | fork_created | [repository](https://github.com/weewx-packages/weewx-modbus-tcp) |
| 135 | [netatmo](https://github.com/Buco7854/weewx-netatmo) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-netatmo) |
| 136 | [nm150](https://github.com/matthewwall/weewx-nm150) | GPL-3.0-or-later (driver only) | blocked_license |  |
| 137 | [owfs](https://github.com/matthewwall/weewx-owfs) | GPL-3.0-or-later AND GPL-3.0-only | hold_successor_license_packaging |  |
| 138 | [rmyro](https://github.com/abillits/weewx-rmyro) | NOASSERTION | blocked_license |  |
| 139 | [sdr](https://github.com/matthewwall/weewx-sdr) | GPL-3.0-only | released | [repository](https://github.com/weewx-packages/weewx-sdr) |
| 140 | [sds011](https://github.com/matthewwall/weewx-sds011) | GPL-3.0-only | resolved_by_successor_release | [repository](https://github.com/weewx-packages/weewx-NovaSDS011) |
| 141 | [swb](https://github.com/matthewwall/weewx-swb) | NOASSERTION | blocked_license |  |
| 142 | [tempestWS](https://github.com/livysdad27/tempestWS) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-tempest-ws) |
| 143 | [tfrc](https://github.com/matthewwall/weewx-tfrc) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-tfrc) |
| 144 | [tracer](https://github.com/matthewwall/weewx-tracer) | GPL-3.0-only | independent_continuation_published | [repository](https://github.com/weewx-packages/weewx-tracer) |
| 145 | [twi](https://github.com/matthewwall/weewx-twi) | NOASSERTION | blocked_distribution_rights |  |
| 146 | [uradmon](https://github.com/glennmckechnie/weewx-uradmon) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-uradmon) |
| 147 | [vedirect](https://github.com/matthewwall/weewx-vedirect) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-vedirect) |
| 148 | [w820](https://github.com/daduke/ventusw820) | GPL-3.0-or-later (README) | released | [repository](https://github.com/weewx-packages/ventusw820) |
| 149 | [wanet](https://sourceforge.net/projects/wariome11) | GPL-3.0-or-later AND GPL-3.0-only | defer_external_import |  |
| 150 | [weatherflowUDP](https://github.com/captain-coredump/weatherflow-udp) | GPL-3.0-only | hold_maintenance_borderline |  |
| 151 | [wh23xx](https://github.com/matthewwall/weewx-wh23xx) | GPL-3.0-only | released | [repository](https://github.com/weewx-packages/weewx-wh23xx) |
| 152 | [wlink](https://github.com/matthewwall/weewx-wlink) | NOASSERTION | blocked_distribution_rights |  |
| 153 | [wmr89](https://github.com/tkeffer/weewx-wmr89) | LGPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-wmr89) |
| 154 | [ws6in1](https://github.com/BobAtchley/weewx-ws6in1) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-ws6in1) |
| 155 | [wxt5x0](https://github.com/matthewwall/weewx-wxt5x0) | GPL-3.0-only | released | [repository](https://github.com/weewx-packages/weewx-wxt5x0) |
| 159 | [ultimate-push](https://github.com/hilman2/weewx-ultimate-push) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-ultimate-push) |
| 165 | [wmII](https://github.com/jardiamj/wmII) | GPL-3.0-only AND LicenseRef-PSF-derived-code | local_configurator_distribution_blocked |  |
| 171 | [airlink](https://github.com/chaunceygardiner/weewx-airlink) | GPL-3.0-or-later AND GPL-3.0-only AND OFL-1.1 | fork_created | [repository](https://github.com/weewx-packages/weewx-airlink) |
| 172 | [airlink forked](https://github.com/evilbunny2008/weewx-airlink) | GPL-3.0-or-later AND GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-airlink-extended) |
| 176 | [rtldavis](https://github.com/weewx-contrib/weewx-rtldavis) | NOASSERTION (wiki upstream); GPL-3.0-only (existing hard fork license file) | already_present_hard_fork | [repository](https://github.com/weewx-packages/weewx-rtldavis) |
| 177 | [si1000](https://github.com/tridge/DavisSi1000) | BSD-2-Clause AND LicenseRef-GPL-2.1-or-later-SDCC-exception AND LicenseRef-Unproven-WeeWX-driver | blocked_distribution_rights |  |
| 184 | [Davis Console Model 6313](https://github.com/WernerKr/davisconsoleapi) | GPL-3.0-or-later AND GPL-3.0-only AND OFL-1.1 | fork_created | [repository](https://github.com/weewx-packages/weewx-davisconsoleapi) |
| 190 | [WeatherLink Live](https://github.com/michael-slx/weewx-weatherlink-live) | MIT | hold_maintenance_borderline |  |
| 191 | [WeatherLink Live JSON](https://github.com/vinceskahan/weewx-weatherlinklive-json) | NOASSERTION | skip_deprecated_unavailable |  |
| 192 | [WeatherLink Live UDP](https://github.com/grebleem/weewx-weatherlinkliveudp) | GPL-3.0-or-later AND GPL-3.0-only | local_successor_fixes_bundle_distribution_blocked |  |
| 193 | [WeatherLink Live UDP and Airlink](https://github.com/WernerKr/weewx-weatherlinkliveudp) | GPL-3.0-or-later AND GPL-3.0-only AND OFL-1.1 AND LicenseRef-Unresolved-bundled-components | blocked_license |  |
| 194 | [WeatherLink Live](https://github.com/Drealine/weatherlinklive-driver-weewx) | Apache-2.0 | hold_maintenance_borderline |  |
| 195 | [WeatherLink Live WLL](https://github.com/jonotaegi/weewx-wll) | GPL-3.0-or-later AND GPL-3.0-only | released | [repository](https://github.com/weewx-packages/weewx-wll) |
| 201 | [ecowittcustom](https://github.com/WernerKr/Ecowitt-or-DAVIS-stations-and-Season-skin) | GPL-3.0-or-later AND GPL-3.0-only AND OFL-1.1 AND LicenseRef-Highcharts AND LicenseRef-Unresolved-bundled-components | blocked_license |  |
| 202 | [ecowittGateway](https://github.com/Millardiang/weewx-ecowittGateway) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-ecowittGateway) |
| 203 | [gw1000](https://github.com/weewx-contrib/weewx-gw1000) | GPL-3.0-or-later AND GPL-2.0-or-later | skip_superseded |  |
| 204 | [Weewx_Ecowitt-Gateway-API_Driver](https://repo.w0chp.net/Chipster/Weewx_Ecowitt-Gateway-API_Driver) | GPL-3.0-only | defer_external_import |  |
| 210 | [MQTTSubscribe](https://github.com/weewx-mqtt/subscribe) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-mqtt-subscribe) |
| 211 | [weewxMQTT](https://github.com/morrowwm/weewxMQTT) | GPL-3.0-or-later (driver); GPL-3.0-only (README) | skip_superseded |  |
| 217 | [observerip](https://github.com/dkmcode/weewx-observerip) | GPL-3.0-only | released | [repository](https://github.com/weewx-packages/weewx-observerip) |
| 218 | [socketlogger](https://github.com/poblabs/weewx-socketlogger) | NOASSERTION | blocked_license |  |
| 224 | [Aggregated Values](https://github.com/evilbunny2008/AggregatedValues) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-aggregated-values) |
| 225 | [airgradient](https://github.com/chaunceygardiner/weewx-airgradient) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-airgradient) |
| 226 | [airQ](https://github.com/roe-dl/weewx-airQ) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-airQ) |
| 227 | [AirVisual](https://github.com/inguy24/weewx-airvisual) | GPL-3.0-only | defer_maintenance |  |
| 228 | [aqi](https://github.com/jonathankoren/weewx-aqi) | GPL-3.0-only | completed | [repository](https://github.com/weewx-packages/weewx-aqi) |
| 229 | [as3935](https://github.com/matthewwall/weewx-as3935) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-as3935) |
| 230 | [bme280wx](https://gitlab.com/wjcarpenter/bme280wx) | BSD-2-Clause | completed_with_tracker_comment_blocker | [repository](https://github.com/weewx-packages/bme280wx) |
| 231 | [cmon](https://github.com/matthewwall/weewx-cmon) | GPL-3.0-only | completed | [repository](https://github.com/weewx-packages/weewx-cmon) |
| 232 | [csv](https://github.com/matthewwall/weewx-csv) | GPL-3.0-only | completed | [repository](https://github.com/weewx-packages/weewx-csv) |
| 233 | [davishealthapi](https://github.com/uajqq/weewx-davishealthapi) | NOASSERTION | blocked_license |  |
| 234 | [DWD](https://github.com/roe-dl/weewx-DWD) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-DWD) |
| 235 | [filepile](https://github.com/tkeffer/filepile) | LGPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-filepile) |
| 236 | [forecasting](https://github.com/chaunceygardiner/weewx-forecast) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-forecast) |
| 237 | [luxtronik](https://github.com/tsoodla/weewx-luxtronik) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-luxtronik) |
| 238 | [Marine Data](https://github.com/inguy24/weewx-noaa_marine_API) | GPL-3.0-only | defer_maintenance |  |
| 239 | [maxbotix](https://github.com/matthewwall/weewx-maxbotix) | GPL-3.0-only | existing_fork_verified | [repository](https://github.com/weewx-packages/weewx-maxbotix) |
| 240 | [MQTTSubscribe](https://github.com/weewx-mqtt/subscribe) | GPL-3.0-only | existing_fork_verified | [repository](https://github.com/weewx-packages/weewx-mqtt-subscribe) |
| 241 | [nmea-xdr](https://github.com/tkeffer/weewx-nmea-xdr) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-nmea-xdr) |
| 242 | [OpenWeather API](https://github.com/inguy24/weewx-openweather_API) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-openweather_API) |
| 243 | [owfs](https://github.com/glennmckechnie/weewx-owfs) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-owfs) |
| 244 | [photovoltaics](https://github.com/roe-dl/weewx-photovoltaics) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-photovoltaics) |
| 245 | [PiSenseHat](https://github.com/sbsrouteur/weewx-PiSenseHat) | MIT | fork_created | [repository](https://github.com/weewx-packages/weewx-PiSenseHat) |
| 246 | [PrecipMeter](https://github.com/roe-dl/weewx-precipmeter) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-precipmeter) |
| 247 | [purple](https://github.com/chaunceygardiner/weewx-purple) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-purple) |
| 248 | [purpleair](https://github.com/bakerkj/weewx-purpleair) | GPL-2.0-or-later | borderline_active_old_items |  |
| 249 | [Reservoir](https://github.com/ziti/weewx-reservoir) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-reservoir) |
| 250 | [sds011](https://github.com/sbsrouteur/weewx-sds011) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-sds011) |
| 251 | [Since Last Archive Accumulator](https://github.com/evilbunny2008/SinceLastArchiveAccumulator) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-since-last-archive-accumulator) |
| 252 | [snmp](https://github.com/roe-dl/weewx-snmp) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-snmp) |
| 253 | [SQM](https://github.com/open-astro/weewx-sqm) | MIT | fork_created | [repository](https://github.com/weewx-packages/weewx-sqm) |
| 254 | [sunduration](https://github.com/Jterrettaz/sunduration) | NOASSERTION | blocked_license |  |
| 255 | [tristar](https://github.com/jim-olsen/weewx_tristar) | NOASSERTION | blocked_license |  |
| 256 | [weewx-nws](https://github.com/chaunceygardiner/weewx-nws) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-nws) |
| 257 | [xtide](https://github.com/chaunceygardiner/weewx-xtide) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-xtide) |
| 258 | [NovaSDS011](https://github.com/weewx-contrib/weewx-NovaSDS011) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-NovaSDS011) |
| 264 | [alltimeSeasons](https://github.com/glennmckechnie/alltimeSeasons) | NOASSERTION | hard_fork_plan_license_review |  |
| 265 | [almanac page for the Standard skin](https://github.com/roe-dl/weewx-skymap-almanac) | GPL-3.0-or-later | existing_fork_verified | [repository](https://github.com/weewx-packages/weewx-skymap-almanac) |
| 266 | [amphibian](https://github.com/matthewwall/weewx-amphibian) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-amphibian) |
| 267 | [bootstrap](https://github.com/brewster76/fuzzy-archer) | GPL-2.0-only | borderline_active_old_items |  |
| 268 | [byteweather](https://github.com/byteinsight/Byteweather) | NOASSERTION | blocked_license |  |
| 269 | [carbonsteel-series](https://github.com/Millardiang/weewx-carbonsteel-series) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-carbonsteel-series) |
| 270 | [celestial](https://github.com/chaunceygardiner/weewx-celestial) | GPL-3.0-only | existing_fork_verified | [repository](https://github.com/weewx-packages/weewx-celestial) |
| 271 | [Conditions](https://github.com/open-astro/weewx-conditions) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-conditions) |
| 272 | [DivumWX](https://github.com/Millardiang/weewx-divumwx) | GPL-3.0-only | existing_fork | [repository](https://github.com/weewx-packages/weewx-divumwx) |
| 273 | [ecowitt_console_emulator](https://github.com/Millardiang/weewx-ecowitt_console_emulator) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-ecowitt_console_emulator) |
| 274 | [exfoliation](https://github.com/chaunceygardiner/weewx-exfoliation) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-exfoliation) |
| 275 | [extended Seasons almanac page](https://github.com/roe-dl/weewx-skymap-almanac) | GPL-3.0-or-later | existing_fork_verified | [repository](https://github.com/weewx-packages/weewx-skymap-almanac) |
| 276 | [Flat](https://github.com/neoground/sofaskin) | MIT | superseded |  |
| 277 | [jas](https://github.com/weewx-extensions/jas) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-jas) |
| 278 | [JSON](https://github.com/teeks99/weewx-json) | GPL-3.0-only | completed | [repository](https://github.com/weewx-packages/weewx-json) |
| 279 | [Metrics](https://github.com/Cosmospacedog/weewx-metrics) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-metrics) |
| 280 | [MesoWX](https://github.com/glennmckechnie/weewx-mesowx) | NOASSERTION | blocked_license_borderline |  |
| 281 | [NeoWX](https://github.com/neoground/neowx) | MIT | superseded |  |
| 282 | [NeoWX Material](https://github.com/seehase/neowx-material) | MIT AND LicenseRef-GPL-unspecified | existing_successor_fork | [repository](https://github.com/weewx-packages/neowx-material) |
| 283 | [Niculskin](https://gitlab.com/ngulden/niculskin) | GPL-2.0-only | completed_with_tracker_comment_blocker | [repository](https://github.com/weewx-packages/niculskin) |
| 284 | [Responsive](https://github.com/Lint-Free-Technology/weewx-responsive-skin) | NOASSERTION | blocked_license |  |
| 285 | [simple](https://github.com/matthewwall/weewx-simple) | NOASSERTION | blocked_license_hard_fork_plan |  |
| 286 | [SteelSeries Weather Gauges](https://github.com/mcrossley/SteelSeries-Weather-Gauges) | GPL-2.0-only | missing_wrapper_borderline_upstream |  |
| 287 | [SVG weather symbols and icons](https://github.com/roe-dl/weathericons) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-weathericons) |
| 288 | [weewx-meteoalarm](https://github.com/Millardiang/weewx-meteoalarm) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-meteoalarm) |
| 289 | [WeeWX Weather App](https://github.com/evilbunny2008/WeeWXWeatherApp) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-weather-app) |
| 290 | [WeeWX-WD](https://github.com/ktrue/weewx-saratoga) | AGPL-3.0-only AND GPL-3.0-or-later AND GPL-2.0-or-later AND Apache-2.0 | fork_created | [repository](https://github.com/weewx-packages/weewx-saratoga) |
| 291 | [weewx-wdc](https://github.com/Daveiano/weewx-wdc) | GPL-3.0-only | borderline_active_old_items |  |
| 292 | [weewx-weatherboard](https://github.com/chaunceygardiner/weewx-weatherboard) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-weatherboard) |
| 296 | [Ecowitt Console Emulator](https://github.com/Millardiang/weewx-ecowitt_console_emulator) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-ecowitt_console_emulator) |
| 302 | [Belchertown (original, version 3)](https://github.com/poblabs/weewx-belchertown) | GPL-3.0-only | existing_fork | [repository](https://github.com/weewx-packages/weewx-belchertown) |
| 303 | [Belchertown (continuation fork, version 2)](https://github.com/uajqq/weewx-belchertown-new) | GPL-3.0-only | superseded |  |
| 304 | [Comprehensive HOWTO for setup](https://github.com/vinceskahan/belchertown-from-scratch) | NOASSERTION | blocked_license |  |
| 308 | [SQL](https://github.com/roe-dl/weewx-sqlupload) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-sqlupload) |
| 312 | [French Standard skin](https://github.com/weewx/weewx/files/2409004/weeWX_v3.8.2-Standard-FR.tar.gz) | NOASSERTION | superseded |  |
| 313 | [Thème graphique standard de weewx en français](https://github.com/weewx/weewx/files/2409004/weeWX_v3.8.2-Standard-FR.tar.gz) | NOASSERTION | superseded |  |
| 314 | [weewx-Weather34](https://github.com/steepleian/weewx-Weather34) | LicenseRef-Weather34-restricted AND CC-BY-NC-ND-4.0 | superseded_license_restricted |  |
| 320 | [weewx-aqi-xtype](https://github.com/weewx-extensions/aqi-xtype) | AGPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-aqi-xtype) |
| 321 | [weewx-xaggs](https://github.com/tkeffer/weewx-xaggs) | LGPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-xaggs) |
| 322 | [weewx-GTS](https://github.com/roe-dl/weewx-GTS) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-GTS) |
| 323 | [weewx-phenology](https://lacusveris.com/Phenology) | GPL-3.0-only AND OFL-1.1 | external_archive_no_git |  |
| 329 | [lastrain](https://github.com/weewx-contrib/lastrain-extension) | Not established | license_blocked |  |
| 330 | [weewx-climate](https://github.com/tkeffer/weewx-climate) | LGPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-climate) |
| 336 | [weewx-skyfield-almanac](https://github.com/roe-dl/weewx-skyfield-almanac) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-skyfield-almanac) |
| 337 | [weewx-skymap-almanac](https://github.com/roe-dl/weewx-skymap-almanac) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-skymap-almanac) |
| 338 | [weewx-easter-almanac-example](https://github.com/roe-dl/weewx-easter-almanac-example) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-easter-almanac-example) |
| 339 | [weewx-skyfield](https://github.com/chaunceygardiner/weewx-skyfield) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-skyfield) |
| 340 | [weewx-celestial](https://github.com/chaunceygardiner/weewx-celestial) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-celestial) |
| 346 | [weewx-postgresql](https://github.com/tkeffer/weewx-postgresql) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-postgresql) |
| 347 | [import-wlk](https://github.com/tkeffer/import-wlk) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-import-wlk) |
| 353 | [RTSP Image](https://github.com/ziti/weewx-rtsp-image) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-rtsp-image) |
| 354 | [sftp (original, last commit 2020-05)](https://github.com/matthewwall/weewx-sftp) | GPL-3.0-only | superseded |  |
| 355 | [sftp (continuation fork)](https://github.com/ziti/weewx-sftp) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-sftp) |
| 356 | [weewx-svg2png](https://github.com/roe-dl/weewx-svg2png) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-svg2png) |
| 357 | [WXgraphic](https://github.com/glennmckechnie/weewx-WXgraphic) | GPL-2.0-or-later AND GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-WXgraphic) |
| 358 | [wxobs](https://github.com/glennmckechnie/weewx-wxobs) | GPL-3.0-only | hold_aged_responded |  |
| 364 | [broadcastWeatherFlowUDP](https://github.com/weewx-contrib/broadcastWeatherFlowUDP) | Not established | license_scope_unclear |  |
| 365 | [crt](https://github.com/matthewwall/weewx-crt) | GPL-3.0-only | completed_available_work | [repository](https://github.com/weewx-packages/weewx-crt) |
| 366 | [cwxn](https://github.com/matthewwall/weewx-cwxn) | GPL-3.0-only | completed_available_work | [repository](https://github.com/weewx-packages/weewx-cwxn) |
| 367 | [emoncms](https://github.com/matthewwall/weewx-emoncms) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-emoncms) |
| 368 | [graphite](https://github.com/ampledata/weewx_graphite) | Apache-2.0 | completed_available_work | [repository](https://github.com/weewx-packages/weewx-graphite) |
| 369 | [idokep](https://github.com/lorantkurthy/weewx-idokep) | Not established | license_blocked |  |
| 370 | [influxdb](https://github.com/matthewwall/weewx-influx) | GPL-3.0-only | completed_available_work | [repository](https://github.com/weewx-packages/weewx-influx) |
| 371 | [knx](https://github.com/AZAZ78/weewx-knx) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-knx) |
| 372 | [mastodon](https://github.com/glennmckechnie/weewx-mastodon) | GPL-3.0-only | hold_aged_responded |  |
| 373 | [Meteo-Services](https://stations.meteo-services.com/wxupdates/EXTENSION) | Not established | external_license_scope_unclear |  |
| 374 | [meteotemplate](https://github.com/matthewwall/weewx-meteotemplate) | GPL-3.0-only | completed_available_work | [repository](https://github.com/weewx-packages/weewx-meteotemplate) |
| 375 | [notifier](https://github.com/teeks99/weewx-notify) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-notify) |
| 376 | [OpenAstro](https://github.com/open-astro) | Not established | organization_index_resolved_duplicates |  |
| 377 | [OpenSenseMap](https://github.com/sbsrouteur/weewx-opensensemap) | MIT | hold_recent_fix |  |
| 378 | [openweathermap](https://github.com/matthewwall/weewx-owm) | GPL-3.0-only | completed_available_work | [repository](https://github.com/weewx-packages/weewx-owm) |
| 379 | [previmeteo](https://github.com/previmeteo/weewx-previmeteo) | Not established | license_blocked |  |
| 380 | [prometheus](https://github.com/sulrich/weewx-prompush) | Apache-2.0 | completed_available_work | [repository](https://github.com/weewx-packages/weewx-prompush) |
| 381 | [pusher](https://github.com/raymondelooff/weewx-pusher) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-pusher) |
| 382 | [RainMachine](https://github.com/sprinkler/rainmachine-weewx) | Not established | license_blocked |  |
| 383 | [Regionalwetter Sachsen-Anhalt](https://github.com/roe-dl/weewx-rwsa) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-rwsa) |
| 384 | [Réseau Static de www.infoclimat.fr](https://github.com/AssociationInfoclimat/StatIC-WeeWX) | Not established | license_blocked |  |
| 385 | [RP5](https://github.com/sapegin-o1eg/weewx-rp5) | Not established | license_blocked_repair_candidate |  |
| 386 | [Skyvex](https://github.com/MichaelStrommer-dreiS/weewx-skyvex) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-skyvex) |
| 387 | [thingspeak](https://github.com/matthewwall/weewx-thingspeak) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-thingspeak) |
| 388 | [twitter](https://github.com/matthewwall/weewx-twitter) | GPL-3.0-only | completed_available_work | [repository](https://github.com/weewx-packages/weewx-twitter) |
| 389 | [weatherbug](https://github.com/matthewwall/weewx-wbug) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-wbug) |
| 390 | [weathercloud](https://github.com/matthewwall/weewx-wcloud) | Not established | license_blocked |  |
| 391 | [wetter](https://github.com/matthewwall/weewx-wetter) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-wetter) |
| 392 | [Wetternetz Sachsen](https://github.com/roe-dl/weewx-wns) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-wns) |
| 393 | [windfinder](https://github.com/matthewwall/weewx-windfinder) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-windfinder) |
| 394 | [windguru](https://github.com/claudobahn/weewx-windguru) | Not established | license_blocked_repair_candidate |  |
| 395 | [wlip-emulator](https://github.com/iiseppi/wlip-emulator) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-wlip-emulator) |
| 396 | [wundergroundLike](https://github.com/smeisens/weewx-wundergroundlike) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-wundergroundlike) |
| 397 | [grid voltage monitoring project uploader](https://github.com/thomaslehmann1234/datenerfassung-ortsnetz-auslastung) | MIT AND GPL-3.0-or-later | true_fork_created | [repository](https://github.com/weewx-packages/weewx-ortsnetz-auslastung) |
| 404 | [loopdata](https://github.com/chaunceygardiner/weewx-loopdata) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-loopdata) |
| 410 | [weepe](https://github.com/w4kus/weewx-weepe) | MIT | true_fork_created | [repository](https://github.com/weewx-packages/weewx-weepe) |
| 411 | [aprs](https://github.com/cavedon/weewx-aprs) | MIT | true_fork_created | [repository](https://github.com/weewx-packages/weewx-aprs) |
| 417 | [mqtt](https://github.com/matthewwall/weewx-mqtt) | GPL-3.0-only | superseded |  |
| 418 | [MQTTPublish](https://github.com/weewx-mqtt/publish) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-mqtt-publish) |
| 419 | [MQTTConfigHA](https://github.com/weewx-mqtt/publish) | GPL-3.0-only | component_covered_by_fork | [repository](https://github.com/weewx-packages/weewx-mqtt-publish) |
| 420 | [MQTTPublishV2](https://github.com/evilbunny2008/MQTTPublishV2) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-mqtt-publish-v2) |
| 422 | [Aggregated Values](https://github.com/evilbunny2008/AggregatedValues) | GPL-3.0-only | true_fork_existing | [repository](https://github.com/weewx-packages/weewx-aggregated-values) |
| 426 | [windy](https://github.com/matthewwall/weewx-windy) | GPL-3.0-only | superseded |  |
| 427 | [windy](https://github.com/Jterrettaz/weewx-windy) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-windy) |
| 433 | [Healthchecks](https://github.com/weewx-extensions/healthchecks) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-healthchecks) |
| 434 | [opsgenie](https://github.com/dcapslock/Weewx-OpsGenie) | Not established | license_blocked_repair_candidate |  |
| 435 | [Pushover](https://github.com/weewx-extensions/pushover) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-pushover) |
| 436 | [zabbix](https://github.com/RandomReaper/weewx-zabbix) | Apache-2.0 | completed_available_work | [repository](https://github.com/weewx-packages/weewx-zabbix) |
| 440 | [SetProcessName](https://github.com/knight-of-ni/WeeWX-SetProcessName) | GPL-3.0-only | true_fork_created | [repository](https://github.com/weewx-packages/weewx-setprocessname) |
| 449 | [WPWeeWX](https://github.com/open-astro/wp-weewx) | GPL-3.0 | fork_created | [repository](https://github.com/weewx-packages/wp-weewx) |

## Additions from the weewx-user group and weewx-contrib

Reviewed on 23 October 2026. These projects appear in the [weewx-user group](https://groups.google.com/g/weewx-user/)
or in the [weewx-contrib](https://github.com/weewx-contrib) organization, but not in the wiki snapshot above.
Actively maintained projects are mirrored (`sync: true`) and packaged from upstream. Orphaned projects
become independent continuations (`sync: false`). Projects without a license grant are not taken over.

| Project | License | Decision | Organization copy |
|---|---|---|---|
| [realtime_gauge-data](https://github.com/weewx-contrib/weewx-realtime_gauge-data) | GPL-3.0-only (LICENSE); GPL-2.0-or-later (installer header) | fork_created | [repository](https://github.com/weewx-packages/weewx-realtime_gauge-data) |
| [stackedwindrose26](https://github.com/Millardiang/weewx-stackedwindrose26) | GPL-3.0-or-later | fork_created | [repository](https://github.com/weewx-packages/weewx-stackedwindrose26) |
| [data-ingest](https://github.com/Millardiang/weewx-data-ingest) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-data-ingest) |
| [mqtt-replicate](https://github.com/weewx-mqtt/replicate) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-mqtt-replicate) |
| [mqtt-plugin-loopdata](https://github.com/weewx-mqtt/plugin-loopdata) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-mqtt-plugin-loopdata) |
| [sds011-mqtt](https://github.com/weewx-contrib/sds011-mqtt) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-sds011-mqtt) |
| [ecowitt_local_http](https://github.com/weewx-contrib/weewx-ecowitt_local_http) | GPL-3.0-only (LICENSE); GPL-2.0-or-later (installer header) | fork_created | [repository](https://github.com/weewx-packages/weewx-ecowitt_local_http) |
| [gw1000](https://github.com/weewx-contrib/weewx-gw1000) | GPL-3.0-only (LICENSE); GPL-2.0-or-later (installer header) | fork_created | [repository](https://github.com/weewx-packages/weewx-gw1000) |
| [dark](https://github.com/dieseld23/weewx-dark) | MIT | fork_created | [repository](https://github.com/weewx-packages/weewx-dark) |
| [extras](https://github.com/bellrichm/WeeWX-Extras) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-extras) |
| [utilities](https://github.com/CameronD73/weewx-utilities) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-utilities) |
| [taptap](https://github.com/matthewwall/weewx-taptap) | GPL-3.0-only (license file and source header) | fork_created | [repository](https://github.com/weewx-packages/weewx-taptap) |
| [Cloud_coverage](https://github.com/Millardiang/weewx-Cloud_coverage) | GPL-3.0-only (LICENSE file and source header) | fork_created | [repository](https://github.com/weewx-packages/weewx-Cloud_coverage) |
| [Belchertown-MQTT-Cloudflare-Tunnel](https://github.com/Millardiang/weewx-Belchertown-MQTT-Cloudflare-Tunnel) | GPL-3.0-only | fork_created | [repository](https://github.com/weewx-packages/weewx-Belchertown-MQTT-Cloudflare-Tunnel) |
| [stackedwindrose](https://github.com/weewx-contrib/stackedwindrose-extension) | GPL-3.0-or-later (source header, no LICENSE file) | fork_created | [repository](https://github.com/weewx-packages/weewx-stackedwindrose) |
| [brultech](https://github.com/tkeffer/weewx-brultech) | GPL-3.0-only | hard_fork_created | [repository](https://github.com/weewx-packages/weewx-brultech) |
| [temperaturnu](https://github.com/LapplandsCohan/weewx-temperaturnu) | GPL-3.0-only | hard_fork_created | [repository](https://github.com/weewx-packages/weewx-temperaturnu) |
| [xcumulative](https://github.com/Millardiang/weewx-xcumulative) | GPL-3.0-or-later | hard_fork_created | [repository](https://github.com/weewx-packages/weewx-xcumulative) |
| [hubitat](https://github.com/dennypage/weewx-hubitat) | BSD-2-Clause (source header, no LICENSE file) | hard_fork_created | [repository](https://github.com/weewx-packages/weewx-hubitat) |
| [time_since](https://github.com/Millardiang/weewx-time_since) | LGPL-3.0-only | hard_fork_created | [repository](https://github.com/weewx-packages/weewx-time_since) |
| [home-assistant](https://github.com/felddy/weewx-home-assistant) | MIT | hard_fork_created | [repository](https://github.com/weewx-packages/weewx-home-assistant) |
| [rsync-metrics](https://github.com/n7qnm/weewx-rsync-metrics) | Not established | blocked_license |  |
| [mem-extension](https://github.com/weewx-contrib/mem-extension) | Not established | blocked_license |  |
