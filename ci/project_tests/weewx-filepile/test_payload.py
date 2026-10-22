"""Exercise file parsing through the registered archive service."""

from types import SimpleNamespace
import pytest
import weewx
from user.filepile import FilePile


def test_mapped_zero_empty_and_metric_conversion(tmp_path):
    source = tmp_path / 'readings'
    source.write_text('ignored line\n temperature = 0\nwindSpeed=3.6\nempty=\n')
    bindings = []
    service = FilePile(SimpleNamespace(bind=lambda *args: bindings.append(args)),
                       {'FilePile': {'filename': str(source), 'unit_system': 'METRIC',
                                     'label_map': {'temperature': 'outTemp'}}})
    event = SimpleNamespace(record={'usUnits': weewx.US, 'dateTime': 100})
    service.new_archive_record(event)
    assert bindings[0][0] == weewx.NEW_ARCHIVE_RECORD
    assert event.record['outTemp'] == pytest.approx(32)
    assert event.record['windSpeed'] == pytest.approx(2.23694, rel=1e-5)
    assert event.record['empty'] is None
    assert event.record['dateTime'] == 100


def test_invalid_value_policy(tmp_path):
    source = tmp_path / 'readings'
    source.write_text('outTemp=broken\nextraTemp1=0\n')
    engine = SimpleNamespace(bind=lambda *args: None)
    service = FilePile(engine, {'FilePile': {'filename': str(source)}})
    with pytest.raises(ValueError):
        service.new_archive_record(SimpleNamespace(record={'usUnits': weewx.US}))
    service.ignore_value_error = True
    event = SimpleNamespace(record={'usUnits': weewx.US})
    service.new_archive_record(event)
    assert event.record['extraTemp1'] == 32
    assert 'outTemp' not in event.record
