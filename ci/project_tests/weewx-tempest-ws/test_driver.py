"""Decode Tempest WebSocket observations and rapid wind packets."""

import json
from unittest.mock import Mock
import weewx
from user.tempestWS import tempestWS


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/tempestWS.py').read_bytes() == (payload / 'bin/user/tempestWS.py').read_bytes()


def test_websocket_observation_and_rapid_wind():
    driver = tempestWS.__new__(tempestWS)
    driver.ws = Mock()
    driver.ws.recv.side_effect = [
        json.dumps({'type': 'obs_st', 'obs': [[1000, 1, 2, 3, 270, 3, 1012.3, -2, 0, 100, 4, 450, 0.2, 0, 12, 2, 2.7, 1]]}),
        json.dumps({'type': 'rapid_wind', 'ob': [1001, 4.5, 315]})]
    packets = driver.genLoopPackets()
    first, rapid = next(packets), next(packets)
    assert first['dateTime'] == 1000
    assert first['usUnits'] == weewx.METRICWX
    assert first['outTemp'] == -2
    assert first['outHumidity'] == 0
    assert first['rain'] == 0.2
    assert first['lightning_distance'] == 12
    assert first['supplyVoltage'] == 2.7
    assert rapid == {'dateTime': 1001, 'usUnits': weewx.METRICWX, 'windSpeed': 4.5, 'windDir': 315}
