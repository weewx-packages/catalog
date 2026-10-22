"""Check WNS field positions and unit conversion without sending an upload."""

import importlib.util
from pathlib import Path
from queue import Queue
import sys
from urllib.parse import parse_qs, urlsplit, unquote

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


def test_protocol_temperature_and_zero_wind(payload):
    module = load(payload, 'wns')
    uploader = module.WnsThread(Queue(), api_key='fixture-key', station=7)
    url = uploader.format_url({'dateTime': 1704067200, 'usUnits': weewx.US,
        'outTemp': 32, 'windSpeed': 0, 'windDir': 0, 'outHumidity': None, 'barometer': 29.92})
    query = parse_qs(urlsplit(url).query)
    fields = query['var'][0].split(';')
    assert fields[:3] == ['7', 'fixture-key', 'WNS_V2.3']
    assert fields[7] == '0.0'
    assert fields[20] == '0.0'
    assert 'None' not in url
