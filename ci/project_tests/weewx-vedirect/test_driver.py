"""Read VE.Direct serial frames and scale electrical observations."""

from unittest.mock import Mock

import pytest
from user.vedirect import VEDirectDriver, VEDirect


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/vedirect.py').read_bytes() == (payload / 'bin/user/vedirect.py').read_bytes()


def test_millivolts_signed_current_zero_and_fault():
    driver = VEDirectDriver.__new__(VEDirectDriver)
    packet = driver._data_to_packet({'V': '13580', 'I': '-250', 'VPV': '56790', 'PPV': '0', 'ERR': '2', 'LOAD': 'OFF'})
    assert packet['V'] == 13.58
    assert packet['I'] == -0.25
    assert packet['VPV'] == 56.79
    assert packet['PPV'] == 0
    assert packet['error'] == 1
    assert packet['load'] == 0
    assert driver._data_to_packet({'SER#': 'EXAMPLE'}) == {}


def test_serial_bytes_frame_checksum():
    receiver = VEDirect('fixture')
    content = b'\r\nV\t13580\r\nI\t-250\r\nChecksum\t'
    frame = content + bytes([(-sum(content)) % 256])
    receiver.ser = Mock()
    receiver.ser.read.side_effect = [bytes([value]) for value in frame + frame] + [b'']
    assert receiver.get_data() == {'V': '13580', 'I': '-250'}
