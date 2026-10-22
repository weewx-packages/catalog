"""Decode CM1 Modbus registers, scaling, status flags and signed sentinels."""

from user.cm1 import CM1
import pytest


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/cm1.py').read_bytes() == (payload / 'bin/user/cm1.py').read_bytes()


def test_modbus_power_wind_and_signed_values():
    assert CM1._decode_power([12500, 18750, 3]) == {
        'battery_voltage': 12.5, 'solar_voltage': 18.75, 'charger_status': 3}
    wind = CM1._decode_wind([0, 123, 2700, 110, 1800, 100, 900, 215, 3150])
    assert wind['wind_speed'] == pytest.approx(12.3)
    assert wind['wind_dir'] == 270
    assert wind['wind_gust_speed'] == pytest.approx(21.5)
    assert CM1._decode_wind([1]*9)['wind_speed'] is None
    assert CM1._to_signed(65535) == -1
    assert CM1._to_calculated(65526) == -1
    assert CM1._to_calculated(55546) is None
