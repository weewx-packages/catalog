"""Check lunar phase geometry, polar daylight and satellite element parsing offline."""

import importlib.util
from pathlib import Path
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


def test_moon_phase_wrap_and_daylight_boundaries(payload):
    module = load(payload, 'wxskyfield')
    sky = object.__new__(module.Sky)
    assert sky.get_moon_phase_index(0) == 0
    assert sky.get_moon_phase_index(90) == 2
    assert sky.get_moon_phase_index(180) == 4
    assert sky.get_moon_phase_index(359) == 0
    assert module.daylight_seconds(100, 200, 0, 86400, lambda: False) == 100
    assert module.daylight_seconds(None, None, 0, 86400, lambda: True) == 86400
    assert module.daylight_seconds(None, None, 0, 86400, lambda: False) == 0


def test_tle_selects_requested_catalog_number(payload):
    module = load(payload, 'wxskyfield')
    text = ('ISS (ZARYA)\n'
            '1 25544U 98067A   24001.00000000  .00016717  00000-0  30157-3 0  9993\n'
            '2 25544  51.6416  58.3717 0003527  47.1010  64.4702 15.49376432430658\n')
    lines = module.tle_lines(text, 25544)
    assert any(line.startswith('1 25544') for line in lines)
    assert any(line.startswith('2 25544') for line in lines)
    with pytest.raises(ValueError, match='catalog number 25544'):
        module.tle_lines(text, 12345)
