"""Run the complete cloud suite and the pinned existing decoder comparisons."""

import json
import subprocess
import sys
import xml.etree.ElementTree as ET


def test_archived_suite(payload, tmp_path):
    """Exercise the release's API, installed engine, SQLite and CLI boundaries."""
    report = tmp_path / 'suite.xml'
    result = subprocess.run([sys.executable, '-m', 'pytest', '-q', str(payload / 'tests'),
                             '--junitxml=' + str(report)], cwd=payload,
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
    cases = ET.parse(report).findall('.//testcase')
    assert len(cases) >= 90, 'The cloud regression suite was not collected'
    assert not any(case.find('skipped') is not None for case in cases)


def test_original_decoders(payload, tmp_path):
    """Run old code in isolated processes against the verified release payload."""
    report = tmp_path / 'oracles.json'
    result = subprocess.run([sys.executable, str(payload / 'tools/oracle_probe.py'),
                             '--download', '--directory', str(tmp_path / 'sources'),
                             '--output', str(report)], cwd=tmp_path,
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
    checks = json.loads(report.read_text())
    assert set(checks) == {'console', 'wlip', 'wll', 'wldc', 'v1'}
    assert sum(len(values) for row in checks.values()
               for values in row['comparisons']) >= 45
