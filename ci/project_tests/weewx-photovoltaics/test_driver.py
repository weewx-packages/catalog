"""Decode RSCP power-meter replies and preserve buffered samples and MQTT records."""

import queue
from unittest.mock import Mock
from user.photovoltaics import BaseThread, WxE3DC, _get_obs_type


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/photovoltaics.py').read_bytes() == (payload / 'bin/user/photovoltaics.py').read_bytes()


def test_solar_thread_buffer_interval_and_mqtt_forwarding():
    thread = BaseThread('fixture', 'RSCP')
    thread.mqtt_queue, thread.mqtt_topic = queue.Queue(), 'solar/fixture'
    thread.last_get_ts = 1000
    samples = [{'time': 1005, 'EMS_POWER_PV': 1500}, {'time': 1010, 'EMS_POWER_PV': 0}]
    for sample in samples:
        thread.put_data(sample)
    actual, interval = thread.get_data()
    assert actual == samples
    assert interval == 10
    assert thread.get_data() == ([], None)
    assert thread.mqtt_queue.get_nowait() == ('solar/fixture', samples[0], 'RSCP')
    assert _get_obs_type('EMS_POWER_PV') == 'emsPowerPv'


def test_rscp_power_meter_channels_preserve_signed_and_zero_readings():
    inverter = WxE3DC.__new__(WxE3DC)
    inverter.sendRequest = Mock(return_value=('PM_DATA', 'Container', [
        ('PM_INDEX', 'Uint16', 2), ('PM_POWER_L1', 'Double64', -125.5),
        ('PM_POWER_L2', 'Double64', 0), ('PM_VOLTAGE_L1', 'Float32', 230.25)]))
    assert inverter.get_PM_data(2) == {
        'PM_2_POWER_L1': -125.5, 'PM_2_POWER_L2': 0, 'PM_2_VOLTAGE_L1': 230.25}
    request = inverter.sendRequest.call_args.args[0]
    assert request[0] == 'PM_REQ_DATA'
    assert request[2][0] == ('PM_INDEX', 'Uint16', 2)
