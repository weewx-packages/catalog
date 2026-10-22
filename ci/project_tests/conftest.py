"""Give project checks the exact release payload and the disposable station."""

import json
import os
from pathlib import Path

import pytest


@pytest.fixture
def payload():
    """Return the checksum-verified archive root, never the source checkout."""
    return Path(os.environ['EXTENSION_PAYLOAD'])


@pytest.fixture
def station():
    """Return the station populated by the original extension installer."""
    return Path(os.environ['EXTENSION_STATION'])


@pytest.fixture
def case():
    """Return the resolved source, release and compatibility test profile."""
    return json.loads(os.environ['CASE_JSON'])
