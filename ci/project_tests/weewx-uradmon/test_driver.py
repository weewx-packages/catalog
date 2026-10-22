"""Convert local uRADMonitor HTTP JSON into archive records."""

import io
import json
from unittest.mock import Mock
import pytest
import weewx
from user import uradmon


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/uradmon.py').read_bytes() == (payload / 'bin/user/uradmon.py').read_bytes()


@pytest.mark.parametrize('model', ['1', '8'])
def test_local_http_json_record_zero_and_optional_values(monkeypatch, model):
    service = uradmon.UradMon.__new__(uradmon.UradMon)
    service.rad_addr, service.udebug, service.rec_interval = '192.0.2.1', False, 5
    service.dbm = Mock()
    raw = {'data': {'id': 'fixture', 'type': model, 'detector': 'SBM20',
                    'cpm': 0, 'temperature': -2.5, 'uptime': 100}}
    if model == '8':
        raw['data'].update(humidity=0, pressure=96000, voc=10, co2=0, ch2o=0.01, pm25=3)
    open_url = Mock(return_value=io.BytesIO(json.dumps(raw).encode()))
    monkeypatch.setattr(uradmon.urllib2, 'urlopen', open_url)
    monkeypatch.setattr(uradmon.time, 'sleep', lambda delay: None)
    service.readdata()
    open_url.assert_called_once_with('http://192.0.2.1/j', timeout=3)
    record = service.dbm.addRecord.call_args.args[0]
    assert record['usUnits'] == weewx.METRIC
    assert record['interval'] == 5
    assert record['utemp'] == -2.5
    assert record['ucpm'] == 0
    assert record['uvolt'] is None
    if model == '8':
        assert record['uhum'] == 0
        assert record['upres'] == 96000
        assert record['unoise'] is None
