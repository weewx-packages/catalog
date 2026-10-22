"""Decode binary WMR89 temperature, humidity-limit and pressure packets."""

import pytest
import weewx
from user.wmr89 import WMR89


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/wmr89.py').read_bytes() == (payload / 'bin/user/wmr89.py').read_bytes()


def test_binary_temperature_humidity_limits_and_pressure():
    driver = WMR89.__new__(WMR89)
    temperature = driver._wmr89_temp_packet(bytes.fromhex('b50b01ff9c00fe7dfd0000'))
    assert temperature['temperature_out'] == -10
    assert temperature['humidity_out'] == 95
    assert temperature['dewpoint_out'] is None
    pressure = driver._wmr89_pressure_packet(bytes.fromhex('b40927e927ea0302e0'))
    assert pressure['pressure'] == pytest.approx(1021.7)
    assert pressure['barometer'] == pytest.approx(1021.8)
    assert pressure['usUnits'] == weewx.METRIC
