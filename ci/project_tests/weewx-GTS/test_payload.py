"""Check thermal sums and fixed-length local solar days."""

import pytest
from user import GTS, dayboundarystats


def test_year_boundaries_and_boiling_point():
    assert GTS.dayOfGTSYear(0, 100) == 0
    assert GTS.dayOfGTSYear(100 + 86400, 100) == 1
    assert GTS.dayOfGTSYear(100 + 200 * 86400, 100) == 150
    assert GTS.boilingTemperatureCC(1013.25) == pytest.approx(99.9743)
    assert GTS.boilingTemperatureCC(800) < 95


def test_solar_days_ignore_dst():
    spans = list(dayboundarystats.genDaySpansWithoutDST(1743202800, 1743462000))
    assert len(spans) == 3
    assert all(span.stop - span.start == 86400 for span in spans)
    assert spans[0].start == 1743202800
