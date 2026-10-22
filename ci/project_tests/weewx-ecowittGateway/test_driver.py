"""Decode Ecowitt TCP sensor bytes, signed values and truncated replies."""

import importlib
import weewx
from unittest.mock import Mock
import pytest


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/weewx-EcowittGateway.py').read_bytes() == (payload / 'bin/user/weewx-EcowittGateway.py').read_bytes()


def test_tcp_live_sensor_bytes_signed_temperature_pressure_and_humidity():
    module = importlib.import_module('user.weewx-EcowittGateway')
    driver = module.EcowittTcpDevice.__new__(module.EcowittTcpDevice)
    driver.unit_system = weewx.METRICWX
    driver.unknown = Mock()
    packet = driver.parse_live_data(bytes.fromhex('02ffce0600092794'))
    assert packet['common_list.0x02.val'] == -5
    assert packet['wh25.inhumi'] == 0
    assert packet['wh25.rel'] == pytest.approx(1013.2)
    assert driver.parse_live_data(bytes.fromhex('02ff')) == {}
