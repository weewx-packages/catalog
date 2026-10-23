"""Check installed ObserverIP examples and observations across the transfer-file boundary."""

import importlib
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
import weecfg
import weecfg.extension
import weewx


@pytest.fixture
def driver_module(station, monkeypatch):
    """Import the installed driver while keeping hardware access in fixtures."""
    monkeypatch.syspath_prepend(str(station / 'bin'))
    user = importlib.import_module('user')
    monkeypatch.setattr(user, '__path__', [str(station / 'bin/user')])
    sys.modules.pop('user.observerip', None)
    observerip = importlib.import_module('user.observerip')
    assert observerip.__file__ is not None
    assert Path(observerip.__file__).resolve() == station / 'bin/user/observerip.py'
    return observerip


def test_install_targets_are_managed(payload, station, case):
    """Reject legacy util destinations before checking the installed example bytes."""
    _, installer = weecfg.get_extension_installer(str(payload))
    paths = weecfg.extension.ExtensionEngine._gen_file_paths(
        str(station), str(payload), installer['files'])
    for source, destination in paths:
        installed_relative = Path(destination).relative_to(station)
        assert installed_relative.parts[:2] == ('bin', 'user') or installed_relative.parts[0] == 'skins', installed_relative
        assert Path(destination).read_bytes() == Path(source).read_bytes()
    assert installer['version'] == case['release']['version']
    for relative in ['conf.d/weatherstation-intercept.conf', 'weatherstation/updateweatherstation.php']:
        original = payload / 'bin/user/observerip_examples/apache' / relative
        installed = station / 'bin/user/observerip_examples/apache' / relative
        assert installed.read_bytes() == original.read_bytes()
    assert not (station / 'util/apache/conf.d/weatherstation-intercept.conf').exists()
    assert not (station / 'util/apache/weatherstation/updateweatherstation.php').exists()
    assert (station / 'bin/user/observerip.py').read_bytes() == (payload / 'bin/user/observerip.py').read_bytes()


def test_manual_example_instructions(payload):
    instructions = (payload / 'README.md').read_text()
    assert 'copies two examples to `bin/user/observerip_examples/apache/`' in instructions
    assert '`conf.d/weatherstation-intercept.conf`' in instructions
    assert 'mode = indirect' in instructions


def test_installed_transfer_file_rain_and_duplicate_observations(driver_module, tmp_path):
    """Exercise real file parsing and LOOP packets without an ObserverIP device."""
    transfer = tmp_path / 'observations.txt'
    driver = driver_module.ObserverIPDriver(mode='indirect', xferfile=str(transfer), max_tries=1)
    values = {field[0]: '0' for field in driver.map.values()}
    values.update(epoch='1792627200', tempf='32.5', baromin='29.92', yearlyrainin='12.50')
    transfer.write_text(''.join('%s=%s\n' % item for item in values.items()))
    first = next(driver.genLoopPackets())
    assert first['usUnits'] == weewx.US
    assert first['outTemp'] == 32.5
    assert first['outHumidity'] == 0.0
    assert first['pressure'] == 29.92
    assert first['dateTime'] == 1792627200
    assert 'rain' not in first
    values.update(epoch='1792627216', yearlyrainin='12.75')
    transfer.write_text(''.join('%s=%s\n' % item for item in values.items()))
    second = next(driver.genLoopPackets())
    assert second['rain'] == 0.25
    assert second['dateTime'] == 1792627216
    assert driver.parse_page(driver.get_data()) == {}


def test_archived_source_suite(payload, station, tmp_path):
    """Run the retained HTTP, UDP and parser fixtures from the exact release."""
    report = tmp_path / 'source-suite.xml'
    env = dict(os.environ, PYTHONPATH=str(station / 'bin'), PYTHONDONTWRITEBYTECODE='1')
    process = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-ra',
                              str(payload / 'tests'), '--junitxml=' + str(report)],
                             cwd=payload, env=env, capture_output=True, text=True, timeout=60)
    assert process.returncode == 0, process.stdout + process.stderr
    cases = ET.parse(report).findall('.//testcase')
    assert len(cases) >= 7
    assert not any(case.find('skipped') is not None for case in cases)
