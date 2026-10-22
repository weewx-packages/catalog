"""Run the installed backfill module against archived SQLite observations."""

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import configobj
import weewx
import weewx.manager


def run_installed(station, arguments):
    """Run Python with only the installed station on its extension import path."""
    return subprocess.run([sys.executable, *arguments], cwd=station,
                          env=dict(os.environ, PYTHONPATH=str(station / 'bin')),
                          capture_output=True, text=True, timeout=60)


def test_installed_module_and_help(payload, station):
    """Require the complete original tool at its managed module entry point."""
    installed = station / 'bin/user/aqi/backfill.py'
    assert installed.read_bytes() == (payload / 'bin/aqi_backfill').read_bytes()
    assert not (station / 'bin/aqi_backfill').exists()
    script = ('import sys; from pathlib import Path; from user.aqi import backfill; '
              'assert Path(backfill.__file__).resolve() == Path(sys.argv[1]).resolve()')
    result = run_installed(station, ['-c', script, str(installed)])
    assert result.returncode == 0, result.stdout + result.stderr
    result = run_installed(station, ['-m', 'user.aqi.backfill', '--help'])
    assert result.returncode == 0, result.stdout + result.stderr
    for option in ['config_file', '--start_time', '--end_time']:
        assert option in result.stdout


def test_real_backfill_cli_range_and_aqi(station, tmp_path):
    """Backfill real AQI rows without loading a station driver or mocking the service."""
    config = configobj.ConfigObj({
        'StdArchive': {'archive_interval': 3600},
        'StdConvert': {'target_unit': 'METRICWX'},
        'AqiService': {
            'standard': {'standard': 'user.aqi.us.AirQualityIndex2024',
                         'data_binding': 'aqi_binding'},
            'air_sensor': {'data_binding': 'wx_binding', 'pm2_5': 'pm2_5'}},
        'DataBindings': {
            'wx_binding': {'database': 'weather', 'table_name': 'custom_archive',
                           'manager': 'weewx.manager.Manager',
                           'schema': {'dateTime': 'INTEGER PRIMARY KEY', 'unrelated': 'TEXT',
                                      'interval': 'INTEGER', 'usUnits': 'INTEGER',
                                      'pm2_5': 'REAL', 'outTemp': 'REAL', 'pressure': 'REAL'}},
            'aqi_binding': {'database': 'aqi', 'table_name': 'archive',
                            'manager': 'weewx.manager.Manager',
                            'schema': 'user.aqi.service.schema'}},
        'Databases': {
            'weather': {'database_name': str(tmp_path / 'weather.sdb'), 'driver': 'weedb.sqlite'},
            'aqi': {'database_name': str(tmp_path / 'aqi.sdb'), 'driver': 'weedb.sqlite'}}})
    with weewx.manager.open_manager_with_config(config, 'wx_binding', initialize=True) as weather:
        for timestamp in range(3600, 93601, 3600):
            weather.addRecord({'dateTime': timestamp, 'unrelated': 'do not use column positions',
                               'interval': 60, 'usUnits': weewx.METRICWX, 'pm2_5': 9.0,
                               'outTemp': 0.0, 'pressure': 1013.25})
    weather_path = tmp_path / 'weather.sdb'
    before = hashlib.sha256(weather_path.read_bytes()).hexdigest()
    config.filename = str(tmp_path / 'backfill.conf')
    config.write()
    result = run_installed(station, ['-m', 'user.aqi.backfill', config.filename,
                                    '--start_time', '90000', '--end_time', '93600'])
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip().endswith('Processed 1 archive records')
    with weewx.manager.open_manager_with_config(config, 'aqi_binding') as aqi:
        rows = list(aqi.genSql('SELECT dateTime, aqi_pm2_5, aqi_pm2_5_category FROM archive'))
    assert rows == [(90000, 50.0, 0)]
    assert hashlib.sha256(weather_path.read_bytes()).hexdigest() == before


def test_pinned_source_suite(payload, station):
    """Retain the release's calculator, conversion, ozone and original backfill checks."""
    report = station / 'aqi-upstream-junit.xml'
    result = subprocess.run([sys.executable, '-m', 'pytest', '-q', str(payload / 'tests'),
                             '--junitxml=' + str(report)], cwd=payload,
                            env=dict(os.environ, PYTHONPATH=os.pathsep.join(
                                map(str, [payload / 'bin', payload]))),
                            capture_output=True, text=True, timeout=120)
    (station / 'aqi-upstream-tests.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    suite = ET.parse(report).getroot()
    assert list(suite.iter('testcase')), result.stdout
    assert not list(suite.iter('skipped')), result.stdout
