"""Run current-API MQTT publisher regressions with the bundled broker fixtures."""

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
                          '-q', *[str(payload / 'bin/user/tests/unit' / name) for name in [
                              'test_abstractpublisher.py', 'test_publisherv1.py', 'test_publisherv2.py',
                              'test_publisherv2mqtt3.py', 'test_template.py']], '--junitxml=' + str(report)],
                         cwd=payload, env=env, text=True, capture_output=True, timeout=180)
    assert run.returncode == 0, run.stdout + run.stderr
    cases = ET.parse(report).findall('.//testcase')
    assert len(cases) >= 60
    assert not any(case.find('skipped') is not None for case in cases)
