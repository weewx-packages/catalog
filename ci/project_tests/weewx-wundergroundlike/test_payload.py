"""Check custom-endpoint registration and archive queueing without starting a thread."""

import importlib.util
from pathlib import Path
from queue import Queue
import sys
from types import SimpleNamespace
from unittest.mock import Mock
from urllib.parse import parse_qs, urlsplit

import configobj
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


def test_custom_endpoint_service_posts_archive_and_formats(payload, monkeypatch):
    module = load(payload, 'wundergroundLike')
    monkeypatch.setattr(weewx.restx.AmbientThread, 'start', lambda self: None)
    monkeypatch.setattr(weewx.manager, 'get_manager_dict_from_config', lambda *args: None)
    engine = Mock()
    config = configobj.ConfigObj({'StdRESTful': {'WundergroundLike': {'enable': 'true',
        'station': 'fixture-id', 'password': 'fixture-password', 'server_url': 'https://example.invalid/weather'}}})
    service = module.WundergroundLike(engine, config)
    engine.bind.assert_called_once_with(weewx.NEW_ARCHIVE_RECORD, service.new_archive_record)
    query = parse_qs(urlsplit(service.archive_thread.format_url({'dateTime': 1704067200,
        'usUnits': weewx.METRICWX, 'outTemp': 0, 'outHumidity': 0})).query)
    assert query['tempf'] == ['32.0']
    assert int(query['humidity'][0]) == 0
    assert query['ID'] == ['fixture-id']
    service.new_archive_record(SimpleNamespace(record={'outTemp': 0}))
    assert service.archive_queue.get_nowait() == {'outTemp': 0}
