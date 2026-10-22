"""Check APRS wire fields and atomic file replacement without a radio."""

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
import weewx


def load(payload, name):
    """Load released runtime bytes directly, avoiding an installed source copy."""
    path = payload / 'bin/user' / (name + '.py')
    spec = importlib.util.spec_from_file_location('user.' + name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert Path(module.__file__).resolve().is_relative_to(payload.resolve())
    return module


def test_aprs_packet_atomic_write_and_missing_fields(payload, tmp_path):
    module = load(payload, 'aprs-formatter')
    engine = SimpleNamespace(bind=lambda *args: None)
    output = tmp_path / 'weather.pkt'
    service = module.APRS(engine, {'APRS': {'output_filename': str(output), 'station_model': 'default'}})
    record = {'dateTime': 1704067200, 'usUnits': weewx.US, 'windDir': 0,
              'windSpeed': 5, 'windGust': 12, 'outTemp': -5,
              'outHumidity': 100, 'rainRate': 0.12, 'barometer': 29.92}
    service._handle_new_archive_record(SimpleNamespace(record=record))
    assert output.read_text() == '_01010000c360s005g012t-05r012h00b10132'
    assert not output.with_suffix('.pkt.tmp').exists()
    service._handle_new_archive_record(SimpleNamespace(record={'dateTime': 1704067200}))
    assert output.read_text() == '_01010000c...s...g...t...'
