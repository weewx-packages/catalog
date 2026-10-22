"""Compute Saratoga derived observations with real unit conversion."""

import pytest
import weewx
import weewx.units
from user.wsxtypes import WSXTypes


def test_saturated_wet_bulb_and_missing_readings():
    xtype = WSXTypes()
    record = {'usUnits': weewx.METRIC, 'outTemp': 20, 'pressure': 1013.25,
              'outHumidity': 100}
    metric = xtype.get_scalar('wet_bulb', record, None)
    assert metric[0] == pytest.approx(20, abs=0.1)
    assert metric[1:] == ('degree_C', 'group_temperature')
    imperial = weewx.units.to_std_system(record, weewx.US)
    assert xtype.get_scalar('wet_bulb', imperial, None)[0] == pytest.approx(68, abs=0.2)
    with pytest.raises(weewx.CannotCalculate):
        xtype.get_scalar('wet_bulb', {'usUnits': weewx.METRIC}, None)
