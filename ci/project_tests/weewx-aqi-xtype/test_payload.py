"""Test EPA breakpoints and actual extension registration."""

from types import SimpleNamespace
import pytest
import weewx.xtypes
from user import aqitype


def test_aqi_concentrations():
    calculator = aqitype.EPAAQI(aqitype.Logger(), 0, None, None)
    for concentration, expected in [(0, 0), (5, 28), (23, 77), (100, 182), (400, 649)]:
        assert calculator.calculate('pm2_5', concentration) == expected
    assert calculator.calculate('pm10', 100) == 73


def test_nowcast_weights_and_missing_data():
    calculator = aqitype.NowCast(aqitype.Logger(), 0, None, None)
    value = calculator.calculate_concentration(3600 * 12, 10, 10,
        [3600 * hour for hour in range(12, 0, -1)], [10] * 12)
    assert value == pytest.approx(10)
