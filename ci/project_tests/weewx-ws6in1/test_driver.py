"""Decode USB ASCII fields and rain totals across resets."""

import pytest
from user.ws6in1 import ws6in1


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/ws6in1.py').read_bytes() == (payload / 'bin/user/ws6in1.py').read_bytes()


def test_usb_ascii_fields_sentinels_and_rain_rollover():
    driver = ws6in1.__new__(ws6in1)
    driver.buff = bytearray(b'-3.5 --.- bad 42 --- ')
    driver.index, driver.bad_values = 0, 0
    assert driver.get_float() == -3.5
    assert driver.get_float() is None
    assert driver.get_float() is None
    assert driver.bad_values == 1
    assert driver.get_int() == 42
    assert driver.get_int() is None
    driver.last_rain = None
    assert driver.rain_delta(12.0) == 0
    assert driver.rain_delta(12.5) == 0.5
    assert driver.rain_delta(0.2) == 0.2
