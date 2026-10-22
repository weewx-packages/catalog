"""Capture Pusher payloads and authentication failures at the client boundary."""

import importlib.util
from pathlib import Path
from queue import Queue
import sys
from unittest.mock import Mock

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


def test_selected_payload_and_failed_auth(payload, monkeypatch):
    module = load(payload, 'wxpusher')
    client = Mock()
    monkeypatch.setattr(module, 'PusherClient', lambda *args, **kwargs: client)
    uploader = module.PusherThread(Queue(), None, '1', 'key', 'secret', 'eu', 'weather', 'archive',
                                   observation_types=['dateTime', 'outTemp', 'rain'])
    uploader.process_record({'dateTime': 1704067200, 'outTemp': 0, 'rain': None, 'unselected': 5}, None)
    client.trigger.assert_called_once_with('weather', 'archive',
        {'dateTime': 1704067200, 'outTemp': 0, 'rain': None})
    client.trigger.side_effect = module.PusherBadAuth('fixture rejection')
    with pytest.raises(module.BadLogin):
        uploader.process_record({'dateTime': 1704067200}, None)
