"""Capture Healthchecks HTTP requests at the transport boundary."""

import importlib.util
from io import BytesIO
from pathlib import Path
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


def test_http_ping_path_body_and_timeout(payload, monkeypatch):
    module = load(payload, 'healthchecks')
    sent = []
    monkeypatch.setattr(module, 'urlopen', lambda request, timeout: sent.append((request, timeout)) or BytesIO())
    module.send_ping('example.invalid', 'fixture-uuid', 9, 'fail', 'Überwachung')
    request, timeout = sent.pop()
    assert request.full_url == 'https://example.invalid/fixture-uuid/fail'
    assert request.data == 'Überwachung'.encode('utf-8')
    assert timeout == 9
    module.send_ping('example.invalid', 'fixture-uuid', 2)
    assert sent[0][0].full_url == 'https://example.invalid/fixture-uuid'
    assert sent[0][0].data is None
