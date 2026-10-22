"""Convert report observations with real WeeWX units and missing values."""

import math
import pytest
import weewx
import weewx.units
from user.carbonsteelseries import UnitHelper


def test_report_temperature_rain_and_nan():
    helper = UnitHelper(weewx.units.Converter(weewx.units.USUnits),
                        weewx.units.Formatter())
    assert helper.convert(0, 'outTemp', weewx.METRIC) == 32
    assert helper.convert(25.4, 'rain', weewx.METRICWX) == pytest.approx(1)
    assert helper.convert(None, 'outTemp', weewx.METRIC) is None
    assert helper.round(float('nan'), 'degree_F') is None
    assert helper.round(float('inf'), 'degree_F') is None
