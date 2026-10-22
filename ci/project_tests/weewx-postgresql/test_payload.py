"""Check SQL translation and real PostgreSQL roundtrips on an isolated Unix socket."""

import glob
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import weedb
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


def test_sql_binding_and_numeric_schema_preserve_case(payload):
    module = load(payload, 'postgresql')
    pgcursor = Mock()
    connection = SimpleNamespace(connection=SimpleNamespace(cursor=lambda: pgcursor), real_as_double=True)
    cursor = module.Cursor(connection)
    cursor.create_table('archive', [('dateTime', 'INTEGER PRIMARY KEY'), ('outTemp', 'REAL')])
    calls = pgcursor.execute.call_args_list
    assert 'DOUBLE PRECISION' in calls[0].args[0]
    assert calls[1].args[1] == ('archive', 'dateTime')
    assert calls[2].args[1] == ('archive', 'outTemp')
    cursor.execute('SELECT outTemp FROM archive WHERE dateTime=?', [1704067200])
    assert pgcursor.execute.call_args.args == ('SELECT outTemp FROM archive WHERE dateTime=%s', (1704067200,))


@pytest.mark.parametrize('state,exception', [('23505', weedb.IntegrityError), ('42P01', weedb.NoTableError), ('08006', weedb.DisconnectError)])
def test_server_sqlstate_mapping(payload, state, exception):
    module = load(payload, 'postgresql')
    class ServerError(module.PGDatabaseError):
        sqlstate = state
    @module._pg_guard
    def fail():
        """Raise the fixture server error through the real exception adapter."""
        raise ServerError('fixture server error')
    with pytest.raises(exception):
        fail()


def test_real_postgresql_database_roundtrip(payload):
    module = load(payload, 'postgresql')
    initdb = shutil.which('initdb')
    bindir = Path(initdb).parent if initdb else Path(sorted(glob.glob('/usr/lib/postgresql/*/bin'))[-1])
    with tempfile.TemporaryDirectory(prefix='weewx-pg-', dir='/tmp') as folder:
        root = Path(folder)
        data = root / 'data'
        subprocess.run([str(bindir / 'initdb'), '-D', str(data), '-A', 'trust', '-U', 'fixtureuser'],
                       capture_output=True, check=True)
        subprocess.run([str(bindir / 'pg_ctl'), '-D', str(data), '-l', str(root / 'server.log'),
                        '-o', "-F -h '' -k " + str(root) + ' -p 55432', '-w', 'start'],
                       capture_output=True, check=True)
        options = dict(host=str(root), port=55432, user='fixtureuser', database_name='fixture_db')
        try:
            module.create(**options)
            connection = module.connect(**options)
            cursor = connection.cursor()
            cursor.create_table('archive', [('dateTime', 'INTEGER PRIMARY KEY'), ('outTemp', 'REAL')])
            cursor.execute('INSERT INTO archive (dateTime,outTemp) VALUES (?,?)', (1704067200, 0.0))
            cursor.execute('SELECT outTemp FROM archive WHERE dateTime=?', (1704067200,))
            assert cursor.fetchone() == (0.0,)
            assert connection.columnsOf('archive') == ['dateTime', 'outTemp']
            assert connection.tables() == ['archive']
            cursor.close()
            connection.close()
            module.drop(**options)
        finally:
            subprocess.run([str(bindir / 'pg_ctl'), '-D', str(data), '-m', 'immediate', '-w', 'stop'],
                           capture_output=True, check=True)
