"""Check signed WeatherLink URLs and the HTTP JSON response boundary."""

import collections
import hashlib
import sqlite3
import os
from pathlib import Path
import subprocess
import sys

import weecfg
import weecfg.extension
from types import SimpleNamespace
from unittest.mock import Mock
from user import davisconsoleapi


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/davisconsoleapi.py').read_bytes() == (payload / 'bin/user/davisconsoleapi.py').read_bytes()


def test_signed_api_url_excludes_history_fields_and_http_json(monkeypatch):
    parameters = collections.OrderedDict([('api-key', 'public-fixture'), ('station-id', 123), ('t', 1000), ('start-timestamp', 1), ('end-timestamp', 2)])
    url = davisconsoleapi.get_current_url(parameters, 'fixture-secret')
    assert url == 'https://api.weatherlink.com/v2/current/123?api-key=public-fixture&api-signature=ccdd66eed13fc8acd67103490b0b8574e3bfed41f7ffa3e2b66316e628ee3856&t=1000'
    response = Mock()
    response.json.return_value = {'sensors': []}
    get = Mock(return_value=response)
    monkeypatch.setattr(davisconsoleapi.requests, 'get', get)
    assert davisconsoleapi.get_json(url, False) == {'sensors': []}
    get.assert_called_once_with(url, timeout=10)


def test_current_json_console_sensor_types_and_zero_humidity():
    console = SimpleNamespace(packet_log=0)
    response = {'sensors': [
        {'data_structure_type': 19, 'data': [{'bar_absolute': 29.5, 'bar_sea_level': 29.92}]},
        {'data_structure_type': 21, 'data': [{'temp_in': 32.0, 'hum_in': 0, 'dew_point_in': -5.0}]}]}
    assert davisconsoleapi.decode_current_json(response, console) == {
        'pressure': 29.5, 'barometer': 29.92, 'inTemp': 32.0,
        'inHumidity': 0, 'inDewpoint': -5.0}


def test_historical_signature_retains_time_window():
    parameters = collections.OrderedDict([
        ('api-key', 'public-fixture'), ('end-timestamp', 2),
        ('start-timestamp', 1), ('station-id', 123), ('t', 1000)])
    url = davisconsoleapi.get_historical_url(parameters, 'fixture-secret')
    assert url == (
        'https://api.weatherlink.com/v2/historic/123?api-key=public-fixture'
        '&start-timestamp=1&end-timestamp=2'
        '&api-signature=63b6fc25c08605dbbbbf7a501218205c33258688ee70e3583d6193740ec50b46&t=1000')


def test_install_targets_are_managed(payload, station):
    """Keep every installed file within the repository client's managed roots."""
    _, installer = weecfg.get_extension_installer(str(payload))
    paths = weecfg.extension.ExtensionEngine._gen_file_paths(
        str(station), str(payload), installer['files'])
    for source, destination in paths:
        relative = Path(destination).relative_to(station)
        assert relative.parts[:2] == ('bin', 'user') or relative.parts[0] == 'skins', relative
        assert Path(destination).read_bytes() == Path(source).read_bytes()
    assert not (station / 'bin/schemas/wview_davisconsoleapi.py').exists()


def test_installed_schema_creates_archive_database(station, tmp_path):
    """Create and write the archive using the binding installed by this package."""
    check = r'''import importlib
from pathlib import Path
import sys
import weecfg
import weewx
import weewx.manager

station, database = map(Path, sys.argv[1:])
_, config = weecfg.read_config(str(station / 'weewx.conf'))
binding_name = config['StdArchive'].get('data_binding', 'wx_binding')
binding = config['DataBindings'][binding_name]
assert binding['schema'] == 'user.wview_davisconsoleapi.schema'
schema = importlib.import_module('user.wview_davisconsoleapi')
assert Path(schema.__file__).resolve() == station / 'bin/user/wview_davisconsoleapi.py'
config['Databases'][binding['database']]['database_name'] = str(database)
with weewx.manager.open_manager_with_config(config, binding_name, initialize=True) as manager:
    assert manager.connection.columnsOf(manager.table_name) == [field[0] for field in schema.table]
    manager.addRecord({'dateTime': 1792627200, 'usUnits': weewx.US, 'interval': 5,
                       'pressure': 29.5, 'inHumidity': 0, 'consoleApiLevelC': 43,
                       'consoleOsVersionC': 'fixture-os'})
    record = manager.getRecord(1792627200)
    assert record['pressure'] == 29.5
    assert record['inHumidity'] == 0
    assert record['consoleApiLevelC'] == 43
    assert record['consoleOsVersionC'] == 'fixture-os'
assert database.is_file()
'''
    env = dict(os.environ, PYTHONPATH=str(station / 'bin'))
    result = subprocess.run([sys.executable, '-c', check, str(station),
                             str(tmp_path / 'console.sdb')], cwd=tmp_path,
                            env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


def test_configure_uses_active_binding_and_preserves_custom_schema(payload, tmp_path):
    """Respect custom archives and keep an existing SQLite database intact."""
    _, installer = weecfg.get_extension_installer(str(payload))
    database = tmp_path / 'existing.sdb'
    with sqlite3.connect(database) as connection:
        connection.execute('CREATE TABLE existing (reading REAL)')
        connection.execute('INSERT INTO existing VALUES (12.5)')
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    bindings = {'wx_binding': {'schema': 'weewx.schemas.wview_extended.schema'},
                'custom_binding': {'schema': 'user.custom_schema.schema',
                                   'database': str(database)}}
    config = {'StdArchive': {'data_binding': 'custom_binding'}, 'DataBindings': bindings}
    assert installer.configure(SimpleNamespace(config_dict=config)) is False
    assert bindings['custom_binding']['schema'] == 'user.custom_schema.schema'
    assert bindings['wx_binding']['schema'] == 'weewx.schemas.wview_extended.schema'
    bindings['custom_binding']['schema'] = 'weewx.schemas.wview_extended.schema'
    assert installer.configure(SimpleNamespace(config_dict=config)) is True
    assert bindings['custom_binding']['schema'] == 'user.wview_davisconsoleapi.schema'
    assert bindings['custom_binding']['database'] == str(database)
    assert bindings['wx_binding']['schema'] == 'weewx.schemas.wview_extended.schema'
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before
