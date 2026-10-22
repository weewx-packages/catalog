"""Run a tide CLI fixture and parse event times, levels and native units."""

import os
import subprocess
import sys
import xml.etree.ElementTree as ET

import datetime
import threading
import weewx
from user.xtide import Configuration, XTidePoller, EventType


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/xtide.py').read_bytes() == (payload / 'bin/user/xtide.py').read_bytes()


def test_tide_cli_csv_time_units_and_non_tide_events(tmp_path):
    csv = ('"Fixture Harbor",2024-07-07,8:12 AM UTC,8.50 ft,"High Tide"\n'
           '"Fixture Harbor",2024-07-07,12:54 PM UTC,,"Sunrise"\n'
           '"Fixture Harbor",2024-07-07,4:31 PM UTC,-0.64 ft,"Low Tide"\n')
    executable = tmp_path / 'tide'
    executable.write_text('#!' + sys.executable + '\nimport sys\nsys.stdout.write(' + repr(csv) + ')\n')
    executable.chmod(0o755)
    cfg = Configuration(threading.Lock(), 'Fixture Harbor', str(executable), 2, [])
    assert XTidePoller.populate_tidal_events(cfg)
    assert len(cfg.events) == 2
    first, second = cfg.events
    assert first.usUnits == weewx.US
    assert first.level == 8.5
    assert first.eventType == EventType.HIGH_TIDE
    assert first.dateTime == datetime.datetime(2024, 7, 7, 8, 12, tzinfo=datetime.timezone.utc).timestamp()
    assert second.level == -0.64
    assert second.eventType == EventType.LOW_TIDE


def test_archived_upstream_runtime_suite(payload, tmp_path):
    """Run the archived runtime tests in a fresh process with no allowed skips."""
    report = tmp_path / 'upstream.xml'
    env = dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join([str(payload / 'bin'), str(payload / 'bin/user'), env.get('PYTHONPATH', '')])
    command = [sys.executable, '-m', 'pytest', '-q', '-ra',
               '--junitxml=' + str(report)]
    command.extend(str(payload / name) for name in ['tests/test_xtide.py'])
    command.extend(['-k', 'not TestRealTide and not TestRealMetricHarmonics'])
    result = subprocess.run(command, cwd=payload, env=env, text=True,
                            capture_output=True, timeout=240)
    assert result.returncode == 0, result.stdout + result.stderr
    cases = ET.parse(report).findall('.//testcase')
    assert cases
    assert all(case.find('skipped') is None for case in cases)
