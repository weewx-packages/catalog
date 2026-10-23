"""Source-level smoke checks for tracked projects that have no project-specific suite."""

import ast
import os
from pathlib import Path
import re

import pytest

LICENSE_FILE = re.compile(r'^(LICENSE|LICENCE|COPYING)', re.I)
LICENSE_TEXT = re.compile(r'General Public License|Permission is hereby granted|'
                          r'Redistribution and use in source and binary forms', re.I)


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
    """Require a license file, or a license grant in a source header."""
    if any(LICENSE_FILE.match(path.name) for path in payload.iterdir()):
        return
    granted = [path for path in python_files(payload)
               if LICENSE_TEXT.search(path.read_text(encoding='utf-8', errors='replace')[:4000])]
    assert granted, 'No license file and no license grant in any Python header'


def test_installer_parses(payload):
    installer = payload / 'install.py'
    if installer.is_file():
        tree = ast.parse(installer.read_bytes(), str(installer))
        assert any(isinstance(node, ast.ClassDef) for node in ast.walk(tree)), 'No installer class'
