"""Convert LPS22 pressure registers into LOOP observations; GPIO is the hardware boundary."""

import importlib
import sys
import types
import datetime
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
import user
import weewx
import weewx.units


def test_pressure_registers_temperature_and_humidity_in_loop(monkeypatch, payload):
    gpio = types.ModuleType('RPi.GPIO')
    package = types.ModuleType('RPi')
    package.GPIO = gpio
    monkeypatch.setitem(sys.modules, 'RPi', package)
    monkeypatch.setitem(sys.modules, 'RPi.GPIO', gpio)
    monkeypatch.setattr(user, '__path__', [str(payload / 'bin/user')])
    module = importlib.import_module('user.PiSense')
    assert module.__file__ == str(payload / 'bin/user/PiSense.py')
    service = module.PiSensewx.__new__(module.PiSensewx)
    service.PrevTime = datetime.datetime.now() - datetime.timedelta(seconds=2)
    service.SkipPressures, service.LastRead = 10, 0
    service.PressBuffer, service.PressCount, service.PressIndex = [], 0, 0
    service.LightInit = False
    service.default_units = weewx.US
    service.pressureKeys, service.temperatureKeys, service.humidityKeys = ['pressure'], ['extraTemp1'], ['outHumidity']
    service.temperature = lambda unused: 25
    service.humidity = lambda unused: 0
    service.address = 0x5c
    registers = {0x27: 3, 0x28: 0, 0x29: 0x80, 0x2a: 0x3e, 0x2b: 0xc4, 0x2c: 0x09}
    service.bus = SimpleNamespace(read_byte_data=lambda address, register: registers[register])
    event = SimpleNamespace(packet={'usUnits': weewx.METRICWX})
    service.new_loop_packet(event)
    assert event.packet['pressure'] == 1000
    assert event.packet['extraTemp1'] == 25
    assert event.packet['outHumidity'] == 0
