"""Check Windy query units and omitted missing readings without external requests."""

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
    module = load(payload, 'windy')
    uploader = module.WindyThread(Queue(), station_password='fixture-password', station_id='7')
    record = {'dateTime': 1704067200, 'usUnits': weewx.METRICWX,
              'outTemp': 0, 'windSpeed': 10, 'windDir': 0, 'outHumidity': 0,
              'rainRate': 0, 'barometer': 1013.25, 'windGust': None}
    query = parse_qs(urlsplit(uploader.format_url(record)).query)
    assert float(query['tempf'][0]) == 32
    assert float(query['windspeedmph'][0]) == pytest.approx(22.3694, abs=0.0001)
    assert query['winddir'] == ['0']
    assert query['stationId'] == ['7']
    assert record['outTemp'] == 0
    assert not any(value == ['None'] for value in query.values())
