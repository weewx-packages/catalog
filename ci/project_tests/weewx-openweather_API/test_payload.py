"""Extract nested weather and air-quality HTTP payloads without credentials."""

import io
import json
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
