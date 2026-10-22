"""Parse form and syslog uploads with numeric, identity and missing-value fields."""

import os
import subprocess
import sys
import xml.etree.ElementTree as ET

from user.ultimatepush import transport


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/ultimatepush/transport.py').read_bytes() == (payload / 'bin/user/ultimatepush/transport.py').read_bytes()


def test_form_and_syslog_sensor_upload_zero_sentinel_and_identity():
    form = transport.parse('?ID=123&tempf=32&humidity=0&extra=--.-')
    values, metadata = transport.numbers(form)
    assert metadata == {'ID': '123'}
    assert values == {'tempf': 32, 'humidity': 0, 'extra': None}
    raw = transport.parse('<165>1 2026-10-22 station rtl_433 - - - {"model":"sensor","temperature_C":-4.5}')
    values, metadata = transport.numbers(raw)
    assert values == {'temperature_C': -4.5}
    assert metadata == {'model': 'sensor'}
    assert transport.parse('{bad json') == {}


def test_archived_upstream_runtime_suite(payload, tmp_path):
    """Run the archived runtime tests in a fresh process with no allowed skips."""
    report = tmp_path / 'upstream.xml'
    env = dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join([str(payload / 'bin'), str(payload / 'bin/user'), env.get('PYTHONPATH', '')])
    command = [sys.executable, '-m', 'pytest', '-q', '-ra',
               '--junitxml=' + str(report)]
    command.extend(str(payload / name) for name in ['tests/test_transport.py', 'tests/test_protocols.py', 'tests/test_mapping.py', 'tests/test_fields.py', 'tests/test_ecowitt_gateway.py'])
    result = subprocess.run(command, cwd=payload, env=env, text=True,
                            capture_output=True, timeout=240)
    assert result.returncode == 0, result.stdout + result.stderr
    cases = ET.parse(report).findall('.//testcase')
    assert cases
    assert all(case.find('skipped') is None for case in cases)
