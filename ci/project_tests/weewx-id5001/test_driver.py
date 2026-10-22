"""Decode Heathkit serial records and reject malformed sensor values."""

import pytest
from user.id5001 import Station


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/id5001.py').read_bytes() == (payload / 'bin/user/id5001.py').read_bytes()


def test_serial_record_temperature_wind_pressure_and_bad_values():
    assert Station._decodeTemperature('T000C') == 32
    assert Station._decodeTemperature('T-10C') == 14
    assert Station._decodeHumidity('H00') == 0
    assert Station._decodeWindSpeed('w016L270D') == pytest.approx(16 / 1.609344, rel=1e-5)
    assert Station._decodeWindDirection('<W016M315D') == 315
    assert Station._decodeBarometer('B1013M') == pytest.approx(1013 / 33.8638866667, rel=1e-5)
    assert Station._decodeBarometer('B0000M') is None
    assert Station._decodeTemperature('TbadC') is None
