"""Source-level smoke checks for tracked projects that have no project-specific suite."""

import ast
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

LICENSE_FILE = re.compile(r'^(LICENSE|LICENCE|COPYING)', re.I)
LICENSE_TEXT = re.compile(r'General Public License|Permission is hereby granted|'
                          r'Redistribution and use in source and binary forms|'
                          r'under the terms of the MIT License', re.I)
README_FILE = re.compile(r'^README', re.I)


@pytest.fixture
def payload():
    """Return the checksum-verified archive root."""
    return Path(os.environ['EXTENSION_PAYLOAD'])


def python_files(root):
    return sorted(path for path in root.rglob('*.py') if '.git' not in path.parts)


def test_python_sources_parse(payload):
    for path in python_files(payload):
        ast.parse(path.read_bytes(), str(path))


def test_license_is_present(payload):
    """Require a license file, or a license grant in a source header or the README."""
    if any(LICENSE_FILE.match(path.name) for path in payload.iterdir()):
        return
    # Some projects grant their license only in the README, e.g. "Distributed
    # under the terms of the MIT License". The wiki audit accepts that as
    # evidence, so the top-level README is searched along with the Python headers.
    readmes = [path for path in payload.iterdir() if path.is_file() and README_FILE.match(path.name)]
    granted = [path for path in python_files(payload) + readmes
               if LICENSE_TEXT.search(path.read_text(encoding='utf-8', errors='replace')[:4000])]
    assert granted, 'No license file and no license grant in any Python header or README'


def test_installer_parses(payload):
    installer = payload / 'install.py'
    if installer.is_file():
        tree = ast.parse(installer.read_bytes(), str(installer))
        assert any(isinstance(node, ast.ClassDef) for node in ast.walk(tree)), 'No installer class'


@pytest.fixture
def station():
    """Return the station populated by the original extension installer."""
    return Path(os.environ['EXTENSION_STATION'])


HOOKS = r"""
import importlib
from pathlib import Path
import sys
import weecfg
from weeutil.weeutil import get_object, option_as_list
station = Path(sys.argv[1])
_, config = weecfg.read_config(str(station / 'weewx.conf'))
for services in config['Engine']['Services'].values():
    for name in option_as_list(services):
        if name.startswith('user.'):
            assert callable(get_object(name)), name
for section in config.values():
    driver = section.get('driver') if hasattr(section, 'get') else None
    if isinstance(driver, str) and driver.startswith('user.'):
        module = importlib.import_module(driver)
        assert hasattr(module, 'loader'), driver
"""


def test_installed_hooks_resolve(station):
    """Resolve every user service and driver the installer added to weewx.conf."""
    if not (station / 'weewx.conf').is_file():
        return
    result = subprocess.run([sys.executable, '-c', HOOKS, str(station)], cwd=station,
                            env=dict(os.environ, PYTHONPATH=str(station / 'bin')),
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
