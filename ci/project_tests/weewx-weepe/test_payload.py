"""Check APRS weather-field formatting without opening an AGWPE connection."""

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


def test_aprs_weather_fields_and_calm_wind(payload):
    module = load(payload, 'weepe')
    service = object.__new__(module.AGWPEWx)
    service._lastWindDir = '180'
    assert service._addWind({'windSpeed': 0, 'windDir': 0}) == '360/000'
    assert service._addWind({'windSpeed': 0, 'windDir': None}) == '360/000'
    assert service._addTemp({'outTemp': -5}) == 't-05'
    assert service._addTemp({'outTemp': None}) == 't...'
    assert service._addOutHumidity({'outHumidity': 100}) == 'h00'
