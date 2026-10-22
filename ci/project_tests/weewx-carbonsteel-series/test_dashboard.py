"""Exercise installed dashboard services, search lists and report generation."""
import inspect
import json
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest
import weecfg
import weewx
import weewx.manager
import weewx.reportengine
import weewx.station
from weeutil.weeutil import get_object


def test_installed_services_and_dashboard(station, caplog):
    _, config = weecfg.read_config(str(station / 'weewx.conf'))
    end = 1751457600
    report = config['StdReport']['CarbonSteelSeries']
    output = station / 'dashboard'
    report['HTML_ROOT'] = str(output)
    report['enable'] = True
    config['StdReport']['Defaults']['unit_system'] = 'METRICWX'
    record = dict(dateTime=end, usUnits=weewx.METRICWX, interval=5,
                  outTemp=20, inTemp=22, outHumidity=60, inHumidity=50,
                  barometer=1015, pressure=1000, altimeter=1015,
                  windSpeed=2, windDir=180, windGust=4, windGustDir=180,
                  rain=0, rainRate=0, radiation=300, UV=2, dewpoint=10,
                  windchill=20, heatindex=20, ET=0)
    caplog.set_level(logging.ERROR)
    bindings = []
    info = weewx.station.StationInfo(**config['Station'])
    with weewx.manager.DBBinder(config) as binder:
        source = binder.get_manager('wx_binding', initialize=True)
        source.addRecord([dict(record, dateTime=stamp) for stamp in
                          range(end - 86400 + 300, end + 1, 300)], update=True)
        source.backfill_day_summary()
        engine = SimpleNamespace(db_binder=binder, stn_info=info,
                                 bind=lambda *args: bindings.append(args))
        realtime = get_object('user.carbonsteelseries.CarbonSteelSeriesRealtime')(engine, config)
        realtime.new_archive_record(SimpleNamespace(record=record))
        realtime.new_loop_packet(SimpleNamespace(packet=record))
        live = json.loads((output / 'realtime.json').read_text())
        assert live['current']['outTemp'] == 20
        assert live['current']['windSpeed'] == 2
        assert live['archiveInterval'] == 300
        assert Path(inspect.getfile(type(realtime))).is_relative_to(station / 'bin')
        assert get_object('user.carbonsteelseries.CarbonSteelSeriesHistory')
        assert weewx.NEW_ARCHIVE_RECORD in {item[0] for item in bindings}
        report_engine = weewx.reportengine.StdReportEngine(config, info, gen_ts=end,
                                                          first_run=True)
        report_engine.run(reports=['CarbonSteelSeries'])
    errors = [entry.getMessage() for entry in caplog.records if entry.levelno >= logging.ERROR]
    assert not errors, '\n'.join(errors)
    for name in ['index.html', 'history.json', 'calendar.json']:
        file = output / name
        assert file.is_file() and file.stat().st_size > 20, str(file)
        if file.suffix == '.json':
            assert json.loads(file.read_text())
    assert '<html' in (output / 'index.html').read_text().lower()

    history = json.loads((output / 'history.json').read_text())
    assert len(history['time']) == 288
    assert history['outTemp'] == [20] * 288
    assert history['windSpeed'] == [2] * 288
