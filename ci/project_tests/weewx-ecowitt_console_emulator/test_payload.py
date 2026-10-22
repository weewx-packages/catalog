"""Check dashboard definitions and vapor pressure from installed runtime."""

import pytest
from user.ecowitt_console_emulator import vpd_kpa, build_dashboard_config


def test_vpd_dry_saturated_and_zero():
    assert vpd_kpa(20, 50) == pytest.approx(1.16914, rel=1e-4)
    assert vpd_kpa(20, 100) == 0
    assert vpd_kpa(0, 0) == pytest.approx(0.6108)
    assert vpd_kpa(None, 50) is None
