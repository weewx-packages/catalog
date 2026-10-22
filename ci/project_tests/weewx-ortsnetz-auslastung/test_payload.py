"""Check grid telemetry JSON, units and upload rate limits without an endpoint."""

import importlib.util
import json
from pathlib import Path
from queue import Queue
import sys

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


def test_grid_payload_units_and_outage(payload):
    module = load(payload, 'ortsnetzauslastunguploader')
    thread = module.RESTThread(Queue(), 8.0, 50.0, 'supplyVoltage', 'none', 'none',
        None, None, None, 'Fixture meter', 'fixture-version')
    body, content_type = thread.get_post_body({'dateTime': 1704067200, 'usUnits': weewx.METRIC, 'supplyVoltage': 230.14})
    data = json.loads(body)
    assert content_type == 'application/json'
    assert data['observed_at'] == '2024-01-01T00:00:00Z'
    assert data['l1_v'] == 230.1
    assert data['l2_v'] == -1
    assert data['latitude'] == 50 and data['longitude'] == 8
    body, _ = thread.get_post_body({'dateTime': 1704067200, 'usUnits': weewx.METRIC, 'supplyVoltage': 0})
    assert json.loads(body)['l1_v'] == 0
    assert not thread.skip_this_post(1000)
    assert thread.skip_this_post(1299)
    assert not thread.skip_this_post(1300)
