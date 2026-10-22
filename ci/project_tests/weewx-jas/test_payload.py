"""Render the installed skin from a real archive with known weather values."""

import html
import json
import logging
import re
import math
import weecfg
import weewx
import weewx.manager
import weewx.reportengine
import weewx.station


def test_weather_report(station, caplog):
    _, config = weecfg.read_config(str(station / 'weewx.conf'))
    report_name = 'jas'
    report = config['StdReport'][report_name]
    output = station / 'rendered'
    report['HTML_ROOT'] = str(output)
    report['enable'] = True
    end = 1751457600
    with weewx.manager.open_manager_with_config(config, 'wx_binding', initialize=True) as manager:
        records = []
        for stamp in range(end - 86400 + 300, end + 1, 300):
            records.append(dict(dateTime=stamp, usUnits=weewx.METRICWX, interval=5,
                outTemp=20, inTemp=22, outHumidity=60, inHumidity=50,
                barometer=1015, pressure=1000, altimeter=1015, windSpeed=2,
                windDir=180, windGust=4, windGustDir=180, rain=0,
                rainRate=0, radiation=300, UV=2, dewpoint=10, windchill=20,
                heatindex=20, ET=0))
        manager.addRecord(records, update=True)
        manager.backfill_day_summary()
    info = weewx.station.StationInfo(**config['Station'])
    caplog.set_level(logging.ERROR)
    engine = weewx.reportengine.StdReportEngine(config, info, gen_ts=end, first_run=True)
    engine.run(reports=[report_name])
    errors = [record.getMessage() for record in caplog.records if record.levelno >= logging.ERROR]
    assert not errors, '\n'.join(errors)
    for name in ['index.html']:
        path = output / name
        assert path.is_file() and path.stat().st_size > 50, str(path)
        text = path.read_text()
        assert '$current' not in text
        if name.endswith('.json'):
            data = json.loads(text)
            assert data
        else:
            assert '<html' in text.lower() or '<!doctype' in text.lower() or name.startswith('metrics')
    data = (output / 'dataload/last24hours.js').read_text()
    series = re.search(r'^\s*pageData\.last24hours_avg\.outTemp_wx_binding = (\[.*\]);$', data, re.M)
    assert series, 'No outdoor-temperature history series'
    temperatures = json.loads(series.group(1))
    assert len(temperatures) == 288
    assert temperatures[-1][0] == end * 1000
    assert all(point[1] == 68.0 for point in temperatures)
