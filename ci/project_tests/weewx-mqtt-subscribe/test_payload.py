"""Exercise MQTT field collection using the actual WeeWX unit converter."""

from types import SimpleNamespace
import pytest
import weewx
from user.mqttsubscribe import CollectData, RecordCache


def test_grouped_wind_conversion_and_flush():
    collector = CollectData(['windSpeed', 'windDir'], weewx.METRICWX)
    assert collector.add_data('windSpeed', {'dateTime': 100, 'usUnits': weewx.METRIC,
                                          'windSpeed': 3.6}) == {}
    assert collector.add_data('windDir', {'dateTime': 101, 'usUnits': weewx.METRIC,
                                        'windDir': 180}) == {}
    old = collector.add_data('windSpeed', {'dateTime': 102, 'usUnits': weewx.METRIC,
                                         'windSpeed': 0})
    assert old['windSpeed'] == pytest.approx(1)
    assert old['windDir'] == 180
    assert old['usUnits'] == weewx.METRICWX
    assert collector.get_data()['windSpeed'] == 0


def test_cached_zero_expiry_and_archive_invalidation():
    cache = RecordCache(SimpleNamespace(trace=lambda *args: None))
    cache.update_value('rain', 0, weewx.METRICWX, 100)
    assert cache.get_value('rain', 109, 10) == 0
    assert cache.get_value('rain', 110, 10) is None
    cache.invalidate_value('rain', 105)
    assert cache.get_value('rain', 104, None) == 0
    assert cache.get_value('rain', 105, None) is None
    with pytest.raises(ValueError):
        cache.update_value('rain', 1, weewx.US, 110)
