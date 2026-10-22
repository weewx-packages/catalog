"""Run bundled MQTT protocol regressions against real WeeWX and fake brokers."""

import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET


def test_bundled_protocol_regressions(payload, station, tmp_path):
    report = tmp_path / 'upstream.xml'
    env = dict(os.environ, PYTHONPATH=':'.join(map(str, [payload / 'bin', station / 'bin', payload / 'bin/user/tests/unit', payload / 'tests'])))
    command = 'import sys,user,pytest; user.__path__.insert(0,sys.argv[1]); raise SystemExit(pytest.main(sys.argv[2:]))'
    run = subprocess.run([sys.executable, '-c', command, str(payload / 'bin/user'),
                          '-q', 'bin/user/tests/unit', '--junitxml=' + str(report)],
                         cwd=payload, env=env, text=True, capture_output=True, timeout=180)
    assert run.returncode == 0, run.stdout + run.stderr
    cases = ET.parse(report).findall('.//testcase')
    assert len(cases) >= 100
    assert not any(case.find('skipped') is not None for case in cases)
