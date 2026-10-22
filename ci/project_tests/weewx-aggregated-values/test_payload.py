"""Check aggregate units and rolling periods in the released service."""

from datetime import datetime
import importlib.util
import logging
import os
from pathlib import Path
import sys
import time

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


def test_aggregate_unit_groups_and_rolling_span(payload):
    module = load(payload, 'AggregatedValues')
    assert module.resolve_obs_group('outTemp', 'avg') == 'group_temperature'
    assert module.resolve_obs_group('outTemp', 'mintime') == 'group_time'
    assert module.resolve_obs_group('rain', 'sum') == 'group_rain'
    assert module.resolve_obs_group('outTemp', 'count') == 'group_count'
    provider = module.TimeSpanProvider(logging.getLogger('test'), 0, 6, 1600000000)
    span = provider.get_timespan({'period': 'last24hours'}, 1704110400)
    assert span.start == 1704024000
    assert span.stop == 1704110400
