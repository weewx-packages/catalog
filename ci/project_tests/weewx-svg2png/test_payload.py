"""Rasterize a local SVG through the released generator and real CairoSVG."""

import importlib.util
from pathlib import Path
import sys

from PIL import Image
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


def test_actual_svg_rasterization(payload, tmp_path):
    module = load(payload, 'svg2png')
    (tmp_path / 'chart.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="4" height="3"><rect width="4" height="3" fill="#ff0000"/></svg>')
    skin = configobj.ConfigObj({'HTML_ROOT': '.', 'SVGtoPNGGenerator': {'chart': {'unsafe': 'false'}}})
    generator = module.SVGtoPNGGenerator({'WEEWX_ROOT': str(tmp_path)}, skin, 1704067200, True, None)
    generator.run()
    with Image.open(tmp_path / 'chart.png') as image:
        assert image.size == (4, 3)
        assert image.convert('RGB').getpixel((2, 1)) == (255, 0, 0)
