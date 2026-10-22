"""Check archived AirLink PM2.5 AQI breakpoints and Davis type-5 field conversion."""

import os
import subprocess
import sys
import xml.etree.ElementTree as ET

import copy
import pytest
from user import airlink


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/airlink.py').read_bytes() == (payload / 'bin/user/airlink.py').read_bytes()


@pytest.mark.parametrize('concentration,expected', [(0,0),(9,50),(35.4,100),(55.4,150),(125.4,200)])
def test_aqi_breakpoints(concentration, expected):
    assert airlink.AQI.compute_pm2_5_aqi(concentration) == expected

def test_type_five_conversion_preserves_distinct_averages():
    values = {'pm_10p0': 11.0, 'pm_10p0_last_1_hour': 12.0,
              'pm_10p0_last_3_hours': 13.0, 'pm_10p0_last_24_hours': 14.0,
              'pm_10p0_nowcast': 15.0, 'data_structure_type': 5}
    response = {'data': {'conditions': [copy.copy(values)]}}
    airlink.convert_data_structure_type_5_to_6(response)
    actual = response['data']['conditions'][0]
    assert actual['data_structure_type'] == 6
    for key, value in values.items():
        if key.startswith('pm_'):
            assert actual[key.replace('10p0', '10')] == value
            assert actual[key] is None


def test_archived_upstream_runtime_suite(payload, tmp_path):
    """Run the archived runtime tests in a fresh process with no allowed skips."""
    report = tmp_path / 'upstream.xml'
    env = dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join([str(payload / 'bin'), str(payload / 'bin/user'), env.get('PYTHONPATH', '')])
    command = [sys.executable, '-m', 'pytest', '-q', '-ra',
               '--junitxml=' + str(report)]
    command.extend(str(payload / name) for name in ['tests/test_airlink.py'])
    command.extend(['-k', 'not matches_weewx_seasons_vocabulary'])
    result = subprocess.run(command, cwd=payload, env=env, text=True,
                            capture_output=True, timeout=240)
    assert result.returncode == 0, result.stdout + result.stderr
    cases = ET.parse(report).findall('.//testcase')
    assert cases
    assert all(case.find('skipped') is None for case in cases)
