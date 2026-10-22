"""Check accumulation, missing samples, and reset on an archive event."""

from types import SimpleNamespace
import pytest
import weewx.units
from user.SinceLastArchiveAccumulator import SinceLastArchiveAccumulatorService


def test_accumulate_and_reset():
    bindings = []
    service = SinceLastArchiveAccumulatorService(
        SimpleNamespace(bind=lambda *args: bindings.append(args)), {})
    for rain, et, expected in [(0.1, 0.01, 0.1), (None, None, 0.1), (0.2, 0.02, 0.3)]:
        event = SimpleNamespace(packet={'rain': rain, 'ET': et})
        service.new_loop_packet(event)
        assert event.packet['rain_since_last_archive'] == pytest.approx(expected)
    assert event.packet['ET_since_last_archive'] == pytest.approx(0.03)
    service.handle_archive_record(SimpleNamespace(record={'dateTime': 100}))
    event = SimpleNamespace(packet={'rain': 0, 'ET': 0})
    service.new_loop_packet(event)
    assert event.packet['rain_since_last_archive'] == 0
    assert event.packet['ET_since_last_archive'] == 0
    assert {item[0] for item in bindings} == {weewx.NEW_LOOP_PACKET, weewx.NEW_ARCHIVE_RECORD}
