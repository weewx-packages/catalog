"""Check Skyvex endpoint selection and Ambient wire formatting without uploading."""

import importlib.util
from pathlib import Path
from queue import Queue
import sys
from urllib.parse import parse_qs, urlsplit

import pytest
import weewx


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
    module = load(payload, 'skyvex')
    uploader = module.SkyvexThread(Queue(), station='fixture-id', password='fixture-password')
    record = {'dateTime': 1704067200, 'usUnits': weewx.METRICWX,
              'outTemp': 0, 'windSpeed': 10, 'windDir': 0, 'outHumidity': 0,
              'rainRate': 0, 'barometer': 1013.25, 'windGust': None}
    assert uploader.server_url == 'https://api.skyvex.org/weatherstation/updateweatherstation.php'
    query = parse_qs(urlsplit(uploader.format_url(record)).query)
    assert query['tempf'] == ['32.0']
    assert float(query['windspeedmph'][0]) == pytest.approx(22.4)
    assert int(query['humidity'][0]) == 0
    assert query['ID'] == ['fixture-id']
    assert record['outTemp'] == 0
    assert not any(value == ['None'] for value in query.values())
