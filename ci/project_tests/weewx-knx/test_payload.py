"""Encode real KNX register values through a recording gateway connection."""

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import configobj
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


def test_knx_register_bytes_and_zero(payload, monkeypatch):
    module = load(payload, 'knx')
    tunnel = Mock()
    monkeypatch.setattr(module, 'KNXIPTunnel', lambda *args: tunnel)
    engine = SimpleNamespace(bind=lambda *args: None)
    config = configobj.ConfigObj({'KNX': {'gateway_ip': '192.0.2.1', 'gateway_port': '3671',
                                         'outTemp': '1/2/3', 'windSpeed': '1/2/4', 'rain': '1/2/5'}})
    service = module.KNX(engine, config)
    service._handle_new_archive_record(SimpleNamespace(record={'outTemp': 20.5, 'windSpeed': 0, 'rain': None}))
    calls = tunnel.group_write.call_args_list
    assert len(calls) == 2
    assert calls[0].args[0] == 0x0A03
    assert bytes(calls[0].args[1]) == bytes.fromhex('0c01')
    assert calls[1].args[0] == 0x0A04
    assert bytes(calls[1].args[1]) == bytes.fromhex('0000')
    tunnel.disconnect.assert_called_once()
