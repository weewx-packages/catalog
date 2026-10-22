"""Check the parallel AirLink variant against its declared legacy AQI table."""

import copy
import pytest
from user import airlink


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/airlink.py').read_bytes() == (payload / 'bin/user/airlink.py').read_bytes()


@pytest.mark.parametrize('concentration,expected', [(0,0),(12,50),(35.4,100),(55.4,150),(150.4,200)])
def test_aqi_breakpoints(concentration, expected):
    assert airlink.AQI.compute_pm2_5_aqi(concentration) == expected

def test_type_five_conversion_preserves_distinct_averages():
    values = {'pm_10p0': 11.0, 'pm_10p0_last_1_hour': 12.0,
              'pm_10p0_last_3_hours': 13.0, 'pm_10p0_last_24_hours': 14.0,
              'pm_10p0_nowcast': 15.0, 'data_structure_type': 5}
    response = {'data': {'conditions': [copy.copy(values)]}}
    airlink.convert_data_structure_type_5_to_6(response)
    actual = response['data']['conditions'][0]
    assert actual['data_structure_type'] == 6
    for key, value in values.items():
        if key.startswith('pm_'):
            assert actual[key.replace('10p0', '10')] == value
            assert actual[key] is None
