"""Decode big-endian Luxtronik TCP replies with signed calculated values."""

import struct
from unittest.mock import Mock
from user.luxtronik import Luxtronik


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/luxtronik.py').read_bytes() == (payload / 'bin/user/luxtronik.py').read_bytes()


def test_tcp_big_endian_signed_calculated_registers():
    service = Luxtronik.__new__(Luxtronik)
    service.hp = Mock()
    service.hp.recv.side_effect = [struct.pack('!i', value) for value in [3004, 0, 3, -25, 0, 1024]]
    service.get_calculated()
    service.hp.send.assert_called_once_with(bytes.fromhex('00000bbc00000000'))
    assert service.calculated == [-25, 0, 1024]
    service.hp.close.assert_called_once()
