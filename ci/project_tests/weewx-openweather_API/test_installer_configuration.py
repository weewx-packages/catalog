"""Exercise payload configuration without letting installer hooks save files.

Only ConfigObj's persistence boundary is blocked. YAML mappings, configuration
updates and database schema changes run through the real installer and WeeWX.
"""

import importlib.util

import configobj
import pytest
import weecfg
import weewx.manager


@pytest.fixture
def installer(payload):
    """Load the verified archive's installer, independently of the source checkout."""
    spec = importlib.util.spec_from_file_location('openweather_payload_installer', payload / 'install.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def config(station):
    """Read the installed station without saving any changes made by a test."""
    _, configuration = weecfg.read_config(str(station / 'weewx.conf'))
    return configuration


@pytest.fixture
def forbid_config_writes(monkeypatch):
    """Reject even a temporary ConfigObj write before it can escape the transaction."""
    def forbidden(*args, **kwargs):
        """Report direct persistence by the installer, including separate files."""
        pytest.fail('Installer must leave configuration persistence to the core transaction')

    monkeypatch.setattr(configobj.ConfigObj, 'write', forbidden)


def test_enhanced_configuration_stays_in_memory(installer, config, station, forbid_config_writes):
    before = (station / 'weewx.conf').read_bytes()
    configurator = installer.OpenWeatherConfigurator(config)
    selected = {'ow_temperature': True, 'ow_humidity': False, 'unknown_field': True}
    result = configurator._write_enhanced_config(config, selected, 'CI_FIXTURE_NOT_A_REAL_KEY_00000000',
                                                {'current_weather': 1234, 'air_quality': 5678})
    assert result is config
    service = config['OpenWeatherService']
    assert service['api_key'] == 'CI_FIXTURE_NOT_A_REAL_KEY_00000000'
    assert service['api_modules']['current_weather']['interval'] == 1234
    temperature = service['field_mappings']['current_weather']['temp']
    assert temperature['database_field'] == 'ow_temperature'
    assert temperature['api_path'] == 'main.temp'
    assert temperature['unit_group'] == 'group_temperature'
    assert service['unit_conversions'] == configurator.api_config['unit_conversions']
    assert configurator.get_database_field_mappings(selected) == {'ow_temperature': 'REAL'}
    assert (station / 'weewx.conf').read_bytes() == before


def test_operational_configuration_stays_in_memory(installer, config, station, forbid_config_writes):
    before = (station / 'weewx.conf').read_bytes()
    installer.loader()._write_service_config(config, {
        'api_key': 'CI_FIXTURE_NOT_A_REAL_KEY_00000000', 'timeout': 17,
        'intervals': {'current_weather': 1234}, 'enabled_modules': ['air_quality']})
    service = config['OpenWeatherService']
    assert service['timeout'] == '17'
    assert service['intervals']['current_weather'] == '1234'
    assert service['modules']['current_weather'] == 'false'
    assert service['modules']['air_quality'] == 'true'
    assert (station / 'weewx.conf').read_bytes() == before


def test_field_selection_stays_in_memory(installer, config, station, forbid_config_writes):
    before = (station / 'weewx.conf').read_bytes()
    configurator = installer.OpenWeatherConfigurator(config)
    configurator._save_field_selection({'ow_temperature': True, 'unknown_field': True})
    selection = config['OpenWeatherService']['field_selection']
    assert selection['selected_fields'] == {'ow_temperature': True}
    assert selection['config_version'] == '1.0'
    assert int(selection['selection_timestamp']) > 0
    assert (station / 'weewx.conf').read_bytes() == before


def test_database_extension_preserves_archive_and_config(installer, config, station, forbid_config_writes):
    """Use the active venv's real CLI and SQLite archive, without a configuration copy."""
    before = (station / 'weewx.conf').read_bytes()
    # The CLI needs the existing binding; new service settings stay in memory.
    config['OpenWeatherService']['ci_unwritten'] = 'memory-only'
    timestamp = 1697846400
    with weewx.manager.open_manager_with_config(config, 'wx_binding') as manager:
        manager.addRecord({'dateTime': timestamp, 'usUnits': 1, 'interval': 5, 'outTemp': 42.0})
    database = installer.DatabaseManager(config)
    assert database.create_database_fields({'ow_ci_schema_probe': 'REAL'}) == 1
    assert database.create_database_fields({'ow_ci_schema_probe': 'REAL'}) == 0
    with weewx.manager.open_manager_with_config(config, 'wx_binding') as manager:
        schema = {column[1]: column[2] for column in manager.connection.genSchemaOf('archive')}
        assert schema['ow_ci_schema_probe'].upper() == 'REAL'
        assert 'ow_temperature' in schema
        assert 'ow_aqi' in schema
        record = manager.getRecord(timestamp)
        assert record['outTemp'] == 42.0
        assert record['ow_ci_schema_probe'] is None
    assert (station / 'weewx.conf').read_bytes() == before
