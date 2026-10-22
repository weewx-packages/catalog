"""Render the installed skin from a real archive with known weather values."""

import html
import json
import logging
import re
import subprocess
import math
import weecfg
import weewx
import weewx.manager
import weewx.reportengine
import weewx.station


def test_weather_report(station, caplog):
    _, config = weecfg.read_config(str(station / 'weewx.conf'))
    report_name = 'WeatherBoardReport'
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
    for name in ['index.html', 'splitflap.html']:
        path = output / name
        assert path.is_file() and path.stat().st_size > 50, str(path)
        text = path.read_text()
        assert '$current' not in text
        if name.endswith('.json'):
            data = json.loads(text)
            assert data
        else:
            assert '<html' in text.lower() or '<!doctype' in text.lower() or name.startswith('metrics')
    page = html.unescape((output / 'index.html').read_text())
    assert re.search(r'id="ro-t"[^>]*>.*?OUTSIDE <span class="ro-u">°F</span>', page, re.S)
    reading = re.search(r'function numericReading\(.*?\n  }', page, re.S)
    paint = re.search(r'function boardPaint\(.*?\n  }', page, re.S)
    assert reading and paint
    # The DOM writers are the boundary; the generated data parser and field
    # bindings execute unchanged against a LoopData JSON response fixture.
    script = """const writes = {}, WB = {show: {}};
const roSet = (key, value) => { writes[key] = value; };
const roWind = () => {}, roBarometer = () => {}, roDate = () => {}, roStatus = () => {};
const gustField = () => 'gust';
""" + reading.group(0) + "\n" + paint.group(0) + """
boardPaint({'current.outTemp.formatted': '68.0'}, true, 'fixture');
if (writes['ro-t'] !== '68.0') throw Error('Outdoor temperature is not 68 F');
boardPaint({'current.outTemp.formatted': '0'}, true, 'fixture');
if (writes['ro-t'] !== '0') throw Error('Zero temperature lost');
boardPaint({'current.outTemp.formatted': '68.0'}, false, 'fixture');
if (writes['ro-t'] !== null) throw Error('Stale temperature displayed');
"""
    result = subprocess.run(['node', '-e', script], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
