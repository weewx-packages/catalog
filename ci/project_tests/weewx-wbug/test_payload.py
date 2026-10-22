"""Check WeatherBug query formatting and byte acknowledgements without uploading."""

import importlib.util
from io import BytesIO
from pathlib import Path
from queue import Queue
import sys
from urllib.parse import parse_qs, urlsplit

import pytest
import weewx
import weewx.restx


def load(payload, name):
    """Load released runtime bytes directly, avoiding an installed source copy."""
    path = payload / 'bin/user' / (name + '.py')
    spec = importlib.util.spec_from_file_location('user.' + name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert Path(module.__file__).resolve().is_relative_to(payload.resolve())
    return module


def test_wire_units_zero_and_missing_observations(payload):
    module = load(payload, 'wbug')
    uploader = module.WeatherBugThread(Queue(), publisher_id='fixture-id', station_number='7', password='fixture-password', latitude=50, longitude=8, manager_dict=None)
    record = {'dateTime': 1704067200, 'usUnits': weewx.US,
              'outTemp': 0, 'windSpeed': 10, 'windDir': 0, 'outHumidity': 0,
              'rainRate': 0, 'barometer': 1013.25, 'windGust': None}
    query = parse_qs(urlsplit(uploader.format_url(record)).query)
    assert query['tempf'] == ['0.0']
    assert query['windspeedmph'] == ['10.0']
    assert query['humidity'] == ['0']
    assert query['ID'] == ['fixture-id']
    assert record['outTemp'] == 0
    assert not any(value == ['None'] for value in query.values())


def test_http_response_bytes(payload):
    module = load(payload, 'wbug')
    uploader = module.WeatherBugThread(Queue(), publisher_id='fixture', station_number='7',
        password='fixture', latitude=50, longitude=8, manager_dict=None)
    uploader.check_response(BytesIO(b'Successfully Received'))
    with pytest.raises(weewx.restx.FailedPost):
        uploader.check_response(BytesIO(b'Invalid station'))
