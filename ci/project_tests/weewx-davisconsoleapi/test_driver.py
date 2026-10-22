"""Check signed WeatherLink URLs and the HTTP JSON response boundary."""

import collections
from types import SimpleNamespace
from unittest.mock import Mock
from user import davisconsoleapi


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/davisconsoleapi.py').read_bytes() == (payload / 'bin/user/davisconsoleapi.py').read_bytes()


def test_signed_api_url_excludes_history_fields_and_http_json(monkeypatch):
    parameters = collections.OrderedDict([('api-key', 'public-fixture'), ('station-id', 123), ('t', 1000), ('start-timestamp', 1), ('end-timestamp', 2)])
    url = davisconsoleapi.get_current_url(parameters, 'fixture-secret')
    assert url == 'https://api.weatherlink.com/v2/current/123?api-key=public-fixture&api-signature=ccdd66eed13fc8acd67103490b0b8574e3bfed41f7ffa3e2b66316e628ee3856&t=1000'
    response = Mock()
    response.json.return_value = {'sensors': []}
    get = Mock(return_value=response)
    monkeypatch.setattr(davisconsoleapi.requests, 'get', get)
    assert davisconsoleapi.get_json(url, False) == {'sensors': []}
    get.assert_called_once_with(url, timeout=10)


def test_current_json_console_sensor_types_and_zero_humidity():
    console = SimpleNamespace(packet_log=0)
    response = {'sensors': [
        {'data_structure_type': 19, 'data': [{'bar_absolute': 29.5, 'bar_sea_level': 29.92}]},
        {'data_structure_type': 21, 'data': [{'temp_in': 32.0, 'hum_in': 0, 'dew_point_in': -5.0}]}]}
    assert davisconsoleapi.decode_current_json(response, console) == {
        'pressure': 29.5, 'barometer': 29.92, 'inTemp': 32.0,
        'inHumidity': 0, 'inDewpoint': -5.0}


def test_historical_signature_retains_time_window():
    parameters = collections.OrderedDict([
        ('api-key', 'public-fixture'), ('end-timestamp', 2),
        ('start-timestamp', 1), ('station-id', 123), ('t', 1000)])
    url = davisconsoleapi.get_historical_url(parameters, 'fixture-secret')
    assert url == (
        'https://api.weatherlink.com/v2/historic/123?api-key=public-fixture'
        '&start-timestamp=1&end-timestamp=2'
        '&api-signature=63b6fc25c08605dbbbbf7a501218205c33258688ee70e3583d6193740ec50b46&t=1000')
