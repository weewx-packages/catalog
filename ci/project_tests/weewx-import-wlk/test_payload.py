"""Decode WLK rain fields and time rollover from binary fixture values."""

from datetime import datetime
import importlib.util
from pathlib import Path
import struct
import sys

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


@pytest.mark.parametrize('collector,expected', [(0x000A, 1.0), (0x100A, 0.1), (0x200A, 0.07874), (0x300A, 0.393701)])
def test_binary_rain_collector_scaling(payload, collector, expected):
    module = load(payload, 'import-wlk')
    wire = struct.pack('<H', collector)
    assert module.decode_rain({'rain': struct.unpack('<H', wire)[0]}, 'rain') == pytest.approx(expected)


def test_timestamp_rollover_and_bad_minutes(payload):
    module = load(payload, 'import-wlk')
    assert module.decode_time(2024, 2, 29, 1440) == int(datetime(2024, 3, 1).timestamp())
    with pytest.raises(ValueError, match='Invalid packed time'):
        module.decode_time(2024, 2, 29, 1441)
    with pytest.raises(ValueError, match='Unknown rain collector'):
        module.decode_rain({'rain': 0xF001}, 'rain')
