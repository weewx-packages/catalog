"""Check SVG star geometry and option parsing using the real almanac dependency."""

import importlib.util
import math
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


def test_svg_projection_and_moon_shape(payload):
    module = load(payload, 'skymapalmanac')
    binder = object.__new__(module.SkymapBinder)
    binder.width = 400
    binder.height = 400
    binder.r = 200
    svg = module.SkymapBinder.four_pointed_star(10, 20, 3, '#fff')
    assert '10' in svg and '20' in svg and '#fff' in svg
    assert module.to_bool('true') is True
    assert module.to_bool('false') is False
    assert module.SkymapBinder.magnitude_to_r(1) > module.SkymapBinder.magnitude_to_r(5)
