"""Map Netatmo dashboard readings and retain zero and missing-sensor distinctions."""

import pytest
import weewx
from user.netatmo import CloudClient, NetatmoDriver


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/netatmo.py').read_bytes() == (payload / 'bin/user/netatmo.py').read_bytes()


def test_dashboard_units_zero_and_lost_sensor():
    units = {'unit': 0, 'windunit': 0, 'pressureunit': 0}
    raw = {'dashboard_data': {'Temperature': -4.5, 'WindStrength': 5, 'CO2': 0}}
    data = CloudClient.extract_data(raw, units)
    assert data['Temperature'] == -4.5
    assert data['WindStrength'] == 5
    assert data['CO2'] == 0
    assert CloudClient.extract_data({}, units) == {}
    labelled = CloudClient.apply_labels(data, 'sensor', 'NAModule1')
    driver = NetatmoDriver.__new__(NetatmoDriver)
    driver.sensor_map = {'outTemp': '*.NAModule1.Temperature', 'windSpeed': '*.NAModule1.WindStrength'}
    packet = driver.data_to_packet(labelled)
    assert packet['usUnits'] == weewx.METRIC
    assert packet['outTemp'] == -4.5
    assert packet['windSpeed'] == 5
