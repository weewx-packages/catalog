"""Build Gill field maps from MCF configuration and convert reported units."""

from unittest.mock import Mock
import pytest
import weewx
from user import gill


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/gill.py').read_bytes() == (payload / 'bin/user/gill.py').read_bytes()


def test_tcp_report_map_and_unit_conversion(tmp_path, monkeypatch):
    config = tmp_path / 'station.mcf'
    config.write_text('<config><device name="MX500"/><category name="Reporting"><param name="Report Format"><reportvalue>RH PRESS TEMP</reportvalue></param></category><category name="Pressure"><param name="Pressure Units"><valuestring>INHG</valuestring></param></category><category name="Temperature"><param name="Temperature Units"><valuestring>F</valuestring></param></category></config>')
    sock = Mock()
    monkeypatch.setattr(gill.socket, 'socket', Mock(return_value=sock))
    driver = gill.Gill('192.0.2.1', 1234, 1, str(config))
    packet = driver.proccess_packet(['0', '29.92', '32'])
    assert packet['usUnits'] == weewx.METRICWX
    assert packet['outHumidity'] == 0
    assert packet['pressure'] == pytest.approx(1013.2075, rel=1e-5)
    assert packet['outTemp'] == 0
    sock.connect.assert_called_once_with(('192.0.2.1', 1234))
