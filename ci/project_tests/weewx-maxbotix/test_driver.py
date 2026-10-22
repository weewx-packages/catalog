"""Read Maxbotix serial range records and derive depth and volume."""

from unittest.mock import Mock

import pytest
import weewx
from user.maxbotix import Sensor, extend_packet


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/maxbotix.py').read_bytes() == (payload / 'bin/user/maxbotix.py').read_bytes()


def test_depth_volume_and_no_reading():
    packet = {}
    extend_packet(packet, 1250, 300, 2.5)
    assert packet == {'depth': 175, 'volume': 437.5}
    empty = {}
    extend_packet(empty, None, 300, 2.5)
    assert empty == {}
    extend_packet(empty, 0, 300, None)
    assert empty == {'depth': 300}


def test_serial_ascii_range_and_missing_target():
    sensor = Sensor('MB7363', 'fixture')
    sensor.serial_port = Mock()
    sensor.serial_port.read.side_effect = [b'R0123\r', b'R9999\r', b'broken']
    assert sensor.get_range() == 123
    assert sensor.get_range() is None
    with pytest.raises(weewx.WeeWxIOError, match='unexpected line'):
        sensor.get_range()
