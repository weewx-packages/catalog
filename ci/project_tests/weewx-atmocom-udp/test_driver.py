"""Decode UDP upload bytes, timestamps and rain-counter resets."""

from user.atmocomudp import AtmocomUDPDriver
import pytest
import weewx


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/atmocomudp.py').read_bytes() == (payload / 'bin/user/atmocomudp.py').read_bytes()


def test_socket_bytes_timestamp_mapping_and_rain_reset():
    driver = AtmocomUDPDriver.__new__(AtmocomUDPDriver)
    driver.raintype, driver.lastrain = ['dailyrainin'], {}
    def packet(rain):
        """Provide a UDP recvfrom result with the requested rain counter."""
        wire = ('GET /weatherstation/updateweatherstation.php?ID=TEST&dateutc=2026-10-22+00%3A00%3A00&tempf=32&dailyrainin=' + rain).encode()
        return driver.parseUDPPacket((wire, ('192.0.2.1', 12345)))
    first = packet('0.25')
    assert first['time_epoch'] == 1792627200
    assert first['dailyrainindelta.TEST'] == '0.00'
    second = packet('0.30')
    actual = driver.buildMyLoopPacket(second, {'outTemp': 'tempf.TEST', 'rain': 'dailyrainindelta.TEST'}, weewx.US)
    assert actual['outTemp'] == 32
    assert actual['rain'] == pytest.approx(0.05)
    assert packet('0.02')['dailyrainindelta.TEST'] == '0.02'
    assert driver.parseUDPPacket((b'unknown', ('192.0.2.1', 12345))) is False
