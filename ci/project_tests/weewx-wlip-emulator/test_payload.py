"""Build Davis LOOP packets and verify bytes and CRC without a listening socket."""

import binascii
import importlib.util
from pathlib import Path
import struct
import sys
import threading
from types import SimpleNamespace

import pytest
import weewx


def load(payload, name):
    """Load released runtime bytes directly, avoiding an installed source copy."""
    path = payload / (name + '.py')
    spec = importlib.util.spec_from_file_location('user.' + name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert Path(module.__file__).resolve().is_relative_to(payload.resolve())
    return module


def test_loop_wire_packet_units_and_crc(payload):
    module = load(payload, 'wlip_emulator')
    emulator = object.__new__(module.WeatherLinkEmulator)
    emulator.lock = threading.Lock()
    emulator.current_loop_packet = {'dateTime': 1704067200, 'usUnits': weewx.METRICWX,
        'outTemp': 20, 'inTemp': 0, 'windSpeed': 0, 'windDir': 270, 'outHumidity': 50,
        'barometer': 1013.25, 'dayRain': 2.54}
    packet = emulator.create_davis_loop_packet()
    assert len(packet) == 99 and packet[:3] == b'LOO'
    assert struct.unpack_from('<h', packet, 12)[0] == 680
    assert struct.unpack_from('<H', packet, 16)[0] == 270
    assert struct.unpack_from('<H', packet, 50)[0] == 10
    assert binascii.crc_hqx(packet, 0) == 0
    assert module.crc16(b'123456789') == 0x31C3
