"""Check file-transfer logic and real Paramiko over a temporary loopback SSH server."""

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
                          '-q', 'tests/test_sftp.py', '--junitxml=' + str(report)],
                         cwd=payload, env=env, text=True, capture_output=True, timeout=180)
    assert run.returncode == 0, run.stdout + run.stderr
    cases = ET.parse(report).findall('.//testcase')
    assert len(cases) >= 30
    assert not any(case.find('skipped') is not None for case in cases)


def test_real_loopback_ssh_sftp(payload, station):
    env = dict(os.environ, PYTHONPATH=':'.join(map(str, [payload / 'bin', station / 'bin'])))
    code = ('import sys,user,runpy; user.__path__.insert(0,sys.argv[1]); '
            'path=sys.argv[2]; sys.argv=[path]; runpy.run_path(path,run_name="__main__")')
    run = subprocess.run([sys.executable, '-c', code, str(payload / 'bin/user'),
                          str(payload / 'tests/integration_sftp.py')],
                         cwd=payload, env=env, text=True, capture_output=True, timeout=90)
    assert run.returncode == 0, run.stdout + run.stderr
    assert 'Testing real Paramiko' in run.stdout
    assert 'OK' in run.stderr
