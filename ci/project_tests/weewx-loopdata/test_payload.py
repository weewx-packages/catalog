"""Check weighted rolling statistics and expiry boundaries in the released code."""

import importlib.util
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


def test_weighted_window_expires_at_boundary_and_keeps_zero(payload):
    module = load(payload, 'loopdata')
    stats = module.ContinuousScalarStats(60)
    stats.addSum(100, 0, weight=2)
    stats.addSum(110, 12, weight=1)
    stats.addSum(120, None)
    stats.addSum(120, float('nan'))
    assert stats.avg == 4
    assert stats.getStatsTuple()[:4] == (0, 100, 12, 110)
    stats.trimExpiredEntries(159)
    assert stats.avg == 4
    stats.trimExpiredEntries(160)
    assert stats.avg == 12
    assert stats.getStatsTuple()[:4] == (12, 110, 12, 110)
    stats.trimExpiredEntries(170)
    assert stats.avg is None
    assert stats.count == 0


def test_ordered_minmax_with_repeated_values(payload):
    module = load(payload, 'loopdata')
    values = module.MinMaxDict()
    for value in [4, -2, 7, 0]:
        values[value] = [value]
    assert values.peekitem(0) == (-2, [-2])
    assert values.peekitem(-1) == (7, [7])
    values.pop(-2)
    assert values.peekitem(0) == (0, [0])
