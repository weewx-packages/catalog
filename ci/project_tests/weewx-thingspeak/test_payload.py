"""Check ThingSpeak field conversion, authentication headers and response bytes."""

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


def test_field_map_converts_and_omits_missing_values(payload):
    module = load(payload, 'thingspeak')
    uploader = module.ThingSpeakThread(Queue(), api_key='fixture-token', augment_record=False,
        fields={'field1': {'obs': 'outTemp', 'units': 'degree_C', 'format': '%.1f'},
                'field2': {'obs': 'rain'}, 'field3': {'obs': 'windGust'}})
    query = parse_qs(urlsplit(uploader.format_url({'dateTime': 1704067200, 'usUnits': weewx.US,
        'outTemp': 32, 'rain': 0, 'windGust': None})).query)
    assert query == {'datetime': ['2024-01-01T00:00:00Z'], 'field1': ['0.0'], 'field2': ['0.0']}
    request = uploader.get_request('https://example.invalid')
    assert dict((key.lower(), value) for key, value in request.header_items())['thingspeakapikey'] == 'fixture-token'


def test_http_response_bytes(payload):
    module = load(payload, 'thingspeak')
    uploader = module.ThingSpeakThread(Queue(), api_key='fixture')
    uploader.check_response(BytesIO(b'123'))
    with pytest.raises(weewx.restx.FailedPost):
        uploader.check_response(BytesIO(b'0'))
