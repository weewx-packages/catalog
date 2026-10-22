"""Validate serial XDR checksums and convert transducer values into LOOP units."""

import importlib
import functools
import operator
import queue
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
import weewx


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/nmea-xdr.py').read_bytes() == (payload / 'bin/user/nmea-xdr.py').read_bytes()


def test_serial_sentence_checksum_and_loop_unit_conversion(monkeypatch):
    module = importlib.import_module('user.nmea-xdr')
    queued = queue.Queue()
    thread = module.XDRThread(queued)
    body = b'IIXDR,C,-5.0,C,Air,P,1.0132,B,Barometer'
    checksum = functools.reduce(operator.xor, body, 0)
    valid = b'$' + body + ('*%02X\r\n' % checksum).encode()
    serial = Mock()
    context = Mock()
    context.__enter__ = Mock(return_value=serial)
    context.__exit__ = Mock(return_value=False)
    incoming = iter([b'', b'$' + body + b'*00\r\n', valid])
    def readline():
        """Feed timeout, invalid checksum and valid NMEA bytes to the reader."""
        line = next(incoming)
        if line == valid:
            thread.keep_running = False
        return line
    serial.readline.side_effect = readline
    monkeypatch.setattr(module.serial, 'Serial', Mock(return_value=context))
    thread.run()
    service = module.XDR.__new__(module.XDR)
    service.queue, service.max_packets = queued, 5
    service.sensor_map = {'outTemp': 'C', 'pressure': 'P'}
    event = SimpleNamespace(packet={'usUnits': weewx.US})
    service.new_loop_packet(event)
    assert event.packet['outTemp'] == 23
    assert event.packet['pressure'] == pytest.approx(29.919783335, rel=1e-8)
