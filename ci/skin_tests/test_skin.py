"""Exercise installed skin code with real WeeWX reports and an isolated archive."""

import importlib
import json
import logging
import math
import os
from pathlib import Path
import sys
from unittest.mock import patch

import pytest
import weecfg
import weecfg.extension
import weewx
import weewx.manager
import weewx.reportengine
import weewx.station


@pytest.fixture(scope='module')
def station():
    """Use the station installed by compatibility.py, never the source checkout."""
    root = Path(os.environ['SKIN_STATION'])
    case = json.loads(os.environ['SKIN_CASE'])
    sys.path.insert(0, str(root / 'bin'))
    import user
    user.__path__.insert(0, str(root / 'bin/user'))
    _, config = weecfg.read_config(str(root / 'weewx.conf'))
    return root, case, config


def test_installer_identity_and_declared_files(station):
    root, case, config = station
    payload = Path(os.environ['SKIN_PAYLOAD'])
    # WeeWX's CLI supplies this legacy alias before loading old installers.
    with patch.dict(sys.modules, {'setup': weecfg.extension}):
        _, installer = weecfg.get_extension_installer(str(payload))
    assert installer['name'] == case['installer_name']
    assert installer['version'] == case['release']['version']
    for destination, sources in installer['files']:
        for source in sources:
            assert (payload / source).is_file(), source
    for name in case['imports']:
        module = importlib.import_module(name)
        assert Path(module.__file__).is_relative_to(root / 'bin'), module.__file__


def test_report_generation(station, caplog):
    root, case, config = station
    # External forecasts and MQTT are separate integrations. The fixture keeps
    # the installed search lists and generators while disabling network features.
    report = config['StdReport'][case['report']]
    output = root / 'rendered'
    report['skin'] = case['skin']
    report['HTML_ROOT'] = str(output)
    extras = report.setdefault('Extras', {})
    extras.update({'forecast_enabled': '0', 'earthquake_enabled': '0', 'aqi_enabled': '0'})
    if case['package'] == 'neowx-material':
        extras['Footer'] = {'update_check': 'off'}
        extras['Appearance'] = {'sections': {'weather': {'type': 'card',
            'items': ['outTemp', 'outHumidity', 'barometer', 'windSpeed', 'rain']}}}
    # DivumWX installs static frontend files directly into its configured web
    # root. Keep that root for its JSON generators and verify both outputs.
    if case['package'] == 'divumwx':
        report['HTML_ROOT'] = str(root / 'public_html/divumwx')
        output = Path(report['HTML_ROOT'])
    end = 1751457600
    config['DatabaseTypes']['SQLite']['SQLITE_ROOT'] = str(root / 'archive')
    with weewx.manager.open_manager_with_config(config, 'wx_binding', initialize=True) as manager:
        records = []
        for stamp in range(end - 172800 + 300, end + 1, 300):
            temperature = 18 + 4 * math.sin(stamp / 3600)
            records.append(dict(dateTime=stamp, usUnits=weewx.METRICWX, interval=5,
                outTemp=temperature, inTemp=22, outHumidity=60, inHumidity=50,
                barometer=1015, pressure=1000, altimeter=1015, windSpeed=2,
                windDir=180, windGust=4, windGustDir=180, rain=0,
                rainRate=0, radiation=300, UV=2, dewpoint=10, windchill=temperature,
                heatindex=temperature, ET=0))
        manager.addRecord(records, update=True)
        manager.backfill_day_summary()
    info = weewx.station.StationInfo(**config['Station'])
    caplog.set_level(logging.ERROR)
    engine = weewx.reportengine.StdReportEngine(config, info, gen_ts=end)
    engine.run(reports=[case['report']])
    errors = [record.getMessage() for record in caplog.records if record.levelno >= logging.ERROR]
    assert not errors, '\n'.join(errors)
    for name in case['outputs']:
        file = output / name
        assert file.is_file() and file.stat().st_size > 20, str(file)
        if file.suffix == '.json':
            json.loads(file.read_text())
    assert any(output.rglob('*.js')), 'No frontend JavaScript was installed'
