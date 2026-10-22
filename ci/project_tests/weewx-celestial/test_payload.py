"""Render live-page configuration using the real WeeWX almanac."""

import importlib.util
from pathlib import Path
import sys

import configobj
import pytest
import weewx
import weewx.almanac


def load(payload, name):
    """Load released runtime bytes directly, avoiding an installed source copy."""
    path = payload / 'bin/user' / (name + '.py')
    spec = importlib.util.spec_from_file_location('user.' + name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert Path(module.__file__).resolve().is_relative_to(payload.resolve())
    return module


def test_live_page_configuration_escaping_and_units(payload):
    module = load(payload, 'celestial_page')
    skin = configobj.ConfigObj({'REPORT_NAME': 'observatory', 'lang': 'en',
        'Extras': {'page_update_pwd': '</script><script>bad()</script>', 'refresh_rate': '5'}})
    page = module.CelestialPage(skin, None)
    almanac = weewx.almanac.Almanac(1704067200, lat=50, lon=8, altitude=100)
    config = page.config_dict(almanac, 'astro/index.html')
    assert config['gen_ts'] == 1704067200
    assert config['station_lat'] == 50
    assert config['root'] == '../'
    assert config['refresh_rate'] == 5
    assert config['report_name'] == 'observatory'
    script = page.config_script(almanac, 'astro/index.html')
    assert script.count('</script>') == 1
    assert r'<\/script>' in script
    assert page._dhms(90061).replace('\u00a0', ' ') == '1 d 1 h'
