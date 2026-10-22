"""Use a TCP reply fixture to test SQM parsing and brightness conversion."""

from types import SimpleNamespace
import pytest
import weecfg
import weewx.manager
from user.weewx_sqm_le.sqm import parse_sqm_response, SQMParseError, median
from user.weewx_sqm_le.service import SQMReader


def test_sqm_protocol_and_derived_values(monkeypatch):
    writes = []
    class Connection:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def sendall(self, data):
            writes.append(data)
        def recv(self, length):
            return b'r,21.60m,0000573478Hz,0000000000c,0000000.000s,031.9C\r\n'
    monkeypatch.setattr('user.weewx_sqm_le.service.socket.create_connection', lambda *a, **k: Connection())
    reader = SQMReader('fixture', 10001, 10, 2, 3, None, None)
    sample = reader._poll_once()
    assert writes == [b'rx']
    assert sample.sqm == 21.6
    assert sample.temp_c == 31.9
    assert sample.nsu == 1
    assert sample.cdm2 == pytest.approx(0.0002474137, rel=1e-5)
    assert 6 < sample.nelm < 7
    reader._record(sample)
    assert reader.latest() == sample
    assert reader.pop_samples() == [sample]
    assert reader.pop_samples() == []
    assert median([10, 2, 4, 8]) == 6
    with pytest.raises(SQMParseError):
        parse_sqm_response('x,21.6m')


def test_station_schema_and_cache(station):
    _, config = weecfg.read_config(str(station / 'weewx.conf'))
    with weewx.manager.open_manager_with_config(config, 'wx_binding') as manager:
        assert {'sqm', 'sqmTemp', 'sqmTime', 'cdm2', 'nsu', 'nelm'} <= set(manager.sqlkeys)
    assert config['SQM-LE']['skyfield_cache'] == str(station / 'archive/skyfield')
