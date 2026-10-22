"""Decode byte fixtures at the serial boundary."""

from types import SimpleNamespace

import pytest
from user.sds011 import SDS011


def test_data_frame():
    # AA C0, PM2.5=123, PM10=456, device ID 1234, checksum, AB.
    frame = bytes.fromhex('aa c0 7b 00 c8 01 12 34 8a ab')
    assert SDS011.parse_data(frame) == pytest.approx([12.3, 45.6])
    assert SDS011._chksum(frame) == 0x8a


def test_serial_query_sends_binary_command():
    writes = []
    sensor = SDS011('fixture')
    sensor.serial_port = SimpleNamespace(write=lambda data: writes.append(data))
    sensor.write_command(SDS011.CMD_QUERY_DATA)
    assert writes == [bytes.fromhex('aa b4 04 00 00 00 00 00 00 00 00 00 00 00 00 ff ff 02 ab')]
