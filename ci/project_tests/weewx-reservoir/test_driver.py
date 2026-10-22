"""Parse reordered USGS RDB rows, missing values and observation time zones."""

import os
import subprocess
import sys
import xml.etree.ElementTree as ET

import datetime
import pytest
from user.reservoir import parse_usgs_rdb


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/reservoir.py').read_bytes() == (payload / 'bin/user/reservoir.py').read_bytes()


def test_rdb_newest_row_reordered_columns_timezone_and_sentinel():
    text = ('# USGS instantaneous data\nagency_cd\tsite_no\tdatetime\ttz_cd\t99_00045\t99_62614\n'
            '5s\t15s\t20d\t6s\t14n\t14n\n'
            'USGS\t123\t2026-10-21 10:00\tEDT\t0.1\t600.5\n'
            'USGS\t123\t2026-10-21 10:15\tEDT\tIce\t601.25\n')
    reading = parse_usgs_rdb(text)
    assert reading.values == {'lakeSurfaceLevel': 601.25}
    assert reading.observed == datetime.datetime(2026, 10, 21, 14, 15, tzinfo=datetime.timezone.utc).timestamp()
    with pytest.raises(ValueError, match='data row'):
        parse_usgs_rdb('# empty\n')


def test_archived_upstream_runtime_suite(payload, tmp_path):
    """Run the archived runtime tests in a fresh process with no allowed skips."""
    report = tmp_path / 'upstream.xml'
    env = dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join([str(payload / 'bin'), str(payload / 'bin/user'), env.get('PYTHONPATH', '')])
    command = [sys.executable, '-m', 'pytest', '-q', '-ra',
               '--junitxml=' + str(report)]
    command.extend(str(payload / name) for name in ['tests/test_reservoir.py'])
    result = subprocess.run(command, cwd=payload, env=env, text=True,
                            capture_output=True, timeout=240)
    assert result.returncode == 0, result.stdout + result.stderr
    cases = ET.parse(report).findall('.//testcase')
    assert cases
    assert all(case.find('skipped') is None for case in cases)
