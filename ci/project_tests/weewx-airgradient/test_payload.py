"""Run archived offline tests with language fixtures from the installed WeeWX core."""

import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


def test_shipped_offline_suite(payload, station):
    # The upstream vocabulary test expects a sibling checkout. Supply only
    # Seasons language data from the station created by the exact core under test.
    language_data = payload.parent / 'weewx/src/weewx_data/skins/Seasons/lang'
    shutil.copytree(station / 'skins/Seasons/lang', language_data, dirs_exist_ok=True)
    report = station / 'upstream-junit.xml'
    result = subprocess.run([sys.executable, '-m', 'pytest', '-q',
                             str(payload / 'tests/test_airgradient.py'),
                             '--confcutdir=' + str(payload / 'tests'),
                             '--junitxml=' + str(report)],
                            cwd=payload, env=dict(os.environ), capture_output=True,
                            text=True, timeout=180)
    (station / 'upstream-tests.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    cases = ET.parse(report).findall('.//testcase')
    assert cases
    assert not any(case.find('skipped') is not None for case in cases)
