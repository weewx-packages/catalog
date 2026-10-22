"""Check Easter dates and provider registration in the real almanac registry."""

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
import weewx
import weewx.almanac
import weewx.almanac


def load(payload, name):
    """Load released runtime bytes directly, avoiding an installed source copy."""
    path = payload / 'bin/user' / (name + '.py')
    spec = importlib.util.spec_from_file_location('user.' + name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert Path(module.__file__).resolve().is_relative_to(payload.resolve())
    return module


@pytest.mark.parametrize('year,day', [(2024,31), (2025,51), (2026,36), (2038,56), (1954,49), (1981,50)])
def test_gregorian_easter(payload, year, day):
    assert load(payload, 'easteralmanac').calc_easter_date(year, True) == day


def test_service_registers_and_removes_provider(payload):
    module = load(payload, 'easteralmanac')
    before = list(weewx.almanac.almanacs)
    service = module.EasterService(SimpleNamespace(), {})
    assert len(weewx.almanac.almanacs) == len(before) + 1
    service.shutDown()
    assert weewx.almanac.almanacs == before


def test_easter_value_in_real_almanac(payload):
    module = load(payload, 'easteralmanac')
    almanac = weewx.almanac.Almanac(1740787200, lat=50, lon=8)
    value = module.EasterAlmanac().get_almanac_data(almanac, 'easter')
    assert datetime.fromtimestamp(value.raw, timezone.utc) == datetime(2025, 4, 20, 12, tzinfo=timezone.utc)
    with pytest.raises(weewx.UnknownType):
        module.EasterAlmanac().get_almanac_data(almanac, 'unprovided_field')
