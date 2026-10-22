"""Count lightning interrupts and convert distances with GPIO and sensor I/O fixtures."""

import importlib
import sys
import types
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
import weewx
import weewx.units


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/as3935.py').read_bytes() == (payload / 'bin/user/as3935.py').read_bytes()


@pytest.fixture
def lightning(monkeypatch):
    """Load the real service with only GPIO and AS3935 hardware I/O replaced."""
    gpio = types.ModuleType('RPi.GPIO')
    gpio.BCM, gpio.IN, gpio.RISING = 11, 1, 31
    for name in ['setmode', 'setup', 'remove_event_detect', 'add_event_detect', 'cleanup']:
        setattr(gpio, name, Mock())
    package = types.ModuleType('RPi')
    package.GPIO = gpio
    monkeypatch.setitem(sys.modules, 'RPi', package)
    monkeypatch.setitem(sys.modules, 'RPi.GPIO', gpio)
    sensor = Mock()
    factory = Mock(return_value=sensor)
    boundary = types.ModuleType('RPi_AS3935')
    boundary.RPi_AS3935 = SimpleNamespace(RPi_AS3935=factory)
    monkeypatch.setitem(sys.modules, 'RPi_AS3935', boundary)
    module = importlib.import_module('user.as3935')
    engine = SimpleNamespace(bind=Mock())
    service = module.AS3935(engine, {'AS3935': {}})
    return module, service, sensor, factory


def test_interrupts_counts_reset_and_distance_units(lightning, monkeypatch):
    module, service, sensor, factory = lightning
    monkeypatch.setattr(module.time, 'sleep', lambda delay: None)
    sensor.get_interrupt.return_value = 8
    for distance in [8, 24]:
        sensor.get_distance.return_value = distance
        service.handle_interrupt(17)
    packet = {'usUnits': weewx.US}
    service.read_data(packet)
    assert packet['lightning_strike_count'] == 2
    assert packet['lightning_distance'] == pytest.approx(16 / 1.609344)
    service.read_data(packet)
    assert packet['lightning_strike_count'] == 0
    assert packet['lightning_distance'] is None
    factory.assert_called_once_with(address=3, bus=1)
    sensor.get_interrupt.return_value = 1
    service.handle_interrupt(17)
    sensor.raise_noise_floor.assert_called_once()
    sensor.get_interrupt.return_value = 4
    service.handle_interrupt(17)
    sensor.set_mask_disturber.assert_called_once_with(True)
