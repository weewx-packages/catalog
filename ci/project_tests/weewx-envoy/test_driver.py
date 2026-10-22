"""Read Envoy HTTP JSON and compute energy increments from lifetime counters."""

import io
import weewx
from user import envoy


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/envoy.py').read_bytes() == (payload / 'bin/user/envoy.py').read_bytes()


def test_http_json_power_and_energy_delta(monkeypatch):
    calls = []
    def open_url(url):
        """Return recorded Envoy bytes at the HTTP boundary."""
        calls.append(url)
        return io.BytesIO(b'{"wattsNow":0,"wattHoursLifetime":1000}')
    monkeypatch.setattr(envoy.urllib.request, 'urlopen', open_url)
    source = envoy.Envoy('example.invalid')
    driver = envoy.EnvoyDriver.__new__(envoy.EnvoyDriver)
    driver.last_total = {}
    packet = driver.sensors_to_fields(source.get_data())
    assert packet['power'] == 0
    assert packet['energy'] is None
    assert calls == ['http://example.invalid/api/v1/production']
    packet = driver.sensors_to_fields({'wattsNow': 250, 'wattHoursLifetime': 1025})
    assert packet['energy'] == 25
    assert driver.sensors_to_fields({'wattHoursLifetime': 3})['energy'] is None
