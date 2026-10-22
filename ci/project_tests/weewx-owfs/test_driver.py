"""Read OWServer byte values and compute counter differences across resets."""

from unittest.mock import Mock
import pytest
from user import owfs


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/owfs.py').read_bytes() == (payload / 'bin/user/owfs.py').read_bytes()


def test_owserver_byte_values_locale_decimal_counter_reset_and_rain(monkeypatch):
    bus = Mock()
    bus.get.side_effect = [b'-3,5', b'100', b'104', b'2', b'10', b'12']
    monkeypatch.setattr(owfs, 'ow', bus)
    assert owfs.gauge('temperature', '/28.123/temperature', {}, 1000) == -3.5
    counters = {}
    assert owfs.counter('rain', '/1d.123/counters.A', counters, 1000) is None
    assert owfs.counter('rain', '/1d.123/counters.A', counters, 1001) == 4
    assert owfs.counter('rain', '/1d.123/counters.A', counters, 1002) is None
    rain = {}
    assert owfs.rainwise_bucket('rain', '/1d.123', rain, 1003) is None
    assert owfs.rainwise_bucket('rain', '/1d.123', rain, 1004) == pytest.approx(0.0508)
    assert bus.get.call_args.args == ('/1d.123/counters.B',)
