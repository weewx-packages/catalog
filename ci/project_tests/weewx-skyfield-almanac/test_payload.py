"""Check horizon geometry and NumPy unit values without ephemeris downloads."""

import importlib.util
import math
from pathlib import Path
import sys

import numpy
import pytest
from skyfield.units import Angle
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


def test_horizon_hour_angle_and_phase_geometry(payload):
    module = load(payload, 'skyfieldalmanac')
    assert float(module._setting_hour_angle(Angle(degrees=0), Angle(degrees=0), 0.0)) == pytest.approx(math.pi / 2)
    assert float(module._rising_hour_angle(Angle(degrees=0), Angle(degrees=0), 0.0)) == pytest.approx(-math.pi / 2)
    assert module.numpy_to_weewx((numpy.float64(4), 'degree_C', 'group_temperature')) == (4.0, 'degree_C', 'group_temperature')
    assert module.hip_to_starname(999999, 'unknown star') == 'unknown star'
