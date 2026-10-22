"""Check the released webhook notifier request without contacting its endpoint."""

import importlib.util
from pathlib import Path
from queue import Queue
import sys

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


def test_configured_notification_request(payload):
    module = load(payload, 'notify')
    uploader = module.NotifyThread(Queue(), None, 'https://example.invalid/ping?station=7')
    url = uploader.format_url({'outTemp': 0})
    assert url == 'https://example.invalid/ping?station=7'
    request = uploader.get_request(url)
    assert request.full_url == url
    assert request.get_method() == 'GET'
