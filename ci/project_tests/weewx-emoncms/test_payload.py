"""Check EmonCMS query units and HTTP response bytes without external requests."""

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


def test_selected_observations_convert_and_preserve_zero(payload):
    module = load(payload, 'emoncms')
    uploader = module.EmonCMSThread(Queue(), token='fixture-token', prefix='roof', node=7,
        obs_to_upload='none', inputs={'outTemp': {'units': 'degree_C', 'format': '%.1f'},
                                    'rain': {'units': 'mm', 'format': '%.2f'},
                                    'outHumidity': {}})
    query = parse_qs(urlsplit(uploader.get_url({'dateTime': 1704067200, 'usUnits': weewx.US,
        'outTemp': 32, 'rain': 0, 'outHumidity': None})).query)
    assert query['apikey'] == ['fixture-token']
    assert query['node'] == ['7']
    assert query['json'] == ['{roof_outTemp_C:0.0,roof_rain_mm:0.00}']
    uploader.check_response(BytesIO(b'OK'))
    with pytest.raises(weewx.restx.FailedPost):
        uploader.check_response(BytesIO(b'invalid token'))
