"""Extract nested weather and air-quality HTTP payloads without credentials."""

import io
import json
import os
import subprocess
import sys
import pytest
from user.openweather import OpenWeatherDataCollector


def test_nested_fields_zero_and_missing(monkeypatch):
    mapping = {'temperature': {'api_path': 'main.temp', 'database_field': 'ow_temp'},
               'weather': {'api_path': 'weather[0].id', 'database_field': 'ow_code'},
               'missing': {'api_path': 'main.absent', 'database_field': 'ow_missing'}}
    config = {'OpenWeatherService': {'field_mappings': {'current_weather': mapping}}}
    collector = OpenWeatherDataCollector('fixture', selected_fields={'current_weather': list(mapping)}, config_dict=config)
    result = collector._extract_weather_data({'main': {'temp': 0}, 'weather': [{'id': 800}]})
    assert result['ow_temp'] == 0
    assert result['ow_code'] == 800
    assert 'ow_missing' not in result
    assert result['ow_weather_timestamp'] > 0
    assert collector._extract_value_from_path({'list': [{'components': {'pm2_5': 12.3}}]},
                                             'list[0].components.pm2_5') == 12.3


def test_installed_field_definitions(station):
    """Load field definitions through the cached installer using only station modules."""
    script = r'''
import importlib.util
from pathlib import Path
import sys
import weecfg
station = Path(sys.argv[1])
installer = station / 'bin/user/installer/OpenWeather/install.py'
spec = importlib.util.spec_from_file_location('installed_openweather_installer', installer)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
definitions = station / 'bin/user/openweather_fields.yaml'
assert Path(module._field_definitions_path(str(installer.parent))) == definitions
assert definitions.is_file()
assert not (station / 'openweather_fields.yaml').exists()
_, config = weecfg.read_config(str(station / 'weewx.conf'))
configurator = module.OpenWeatherConfigurator(config)
temperature = configurator.field_definitions['ow_temperature']
assert temperature['api_path'] == 'main.temp'
assert temperature['unit_group'] == 'group_temperature'
assert temperature['database_field'] == 'ow_temperature'
'''
    result = subprocess.run([sys.executable, '-c', script, str(station)], cwd=station,
                            env=dict(os.environ, PYTHONPATH=str(station / 'bin')),
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
