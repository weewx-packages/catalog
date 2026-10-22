"""Check Zambretti forecast behavior at fixed pressure, wind and trend."""

from user.forecast import ZambrettiCode


def test_pressure_trend_and_wind():
    assert ZambrettiCode(1013.0, 0, 0, 1) == 'B'
    assert ZambrettiCode(1013.0, 0, 0, 0) == 'B'
    assert ZambrettiCode(1013.0, 0, 0, -1) == 'H'
    assert ZambrettiCode(1013.0, 0, 2, 1) == 'C'
    assert ZambrettiCode(1013.0, 0, 2, 0) == 'B'
