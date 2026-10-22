"""Check WMO significance precedence and derive past-weather codes."""

from user.precipmeter import max_ww, max_wawa, get_w1w2_from_ww, is_ww_wawa_precipitation


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/precipmeter.py').read_bytes() == (payload / 'bin/user/precipmeter.py').read_bytes()


def test_weather_significance_precedence_and_past_weather():
    assert max_ww([None, 17, 28, 40, 49]) == 17
    assert max_ww([28, 40]) == 28
    assert max_ww([17, 28, 61]) == 61
    assert max_ww([]) is None
    assert max_wawa([None, 40, 61]) == 61
    assert get_w1w2_from_ww([61, 71, 80]) == (8, 7, 6)
    assert is_ww_wawa_precipitation(49, 39) is False
    assert is_ww_wawa_precipitation(50, None) is True
