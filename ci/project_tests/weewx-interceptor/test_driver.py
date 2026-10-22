"""Parse Weather Underground uploads and compute rain increments."""

import pytest
import weewx
from user.interceptor import WUClient


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/interceptor.py').read_bytes() == (payload / 'bin/user/interceptor.py').read_bytes()


def test_wu_query_temperature_rain_increments_and_zero():
    parser = WUClient.Parser()
    def packet(total):
        """Provide an HTTP upload with the requested cumulative rainfall."""
        return parser.parse('ID=TEST&dateutc=2026-10-22+00%3A00%3A00&tempf=32&humidity=0&yearlyrainin='+total+'&dailyrainin='+total)
    first, second = packet('1.25'), packet('1.30')
    assert first['dateTime'] == 1792627200
    assert first['usUnits'] == weewx.US
    assert first['temperature_out'] == 32
    assert first['humidity_out'] == 0
    assert first['rain'] is None
    assert second['rain'] == pytest.approx(0.05)
