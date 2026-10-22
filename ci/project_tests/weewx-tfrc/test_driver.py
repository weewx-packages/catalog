"""Parse tfrec sensor lines with identity, temperature and battery state."""

import weewx
from user.tfrc import TFA_1Packet


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/tfrc.py').read_bytes() == (payload / 'bin/user/tfrc.py').read_bytes()


def test_tfrec_record_sensor_identity_and_negative_temperature():
    lines = ['#1234 1485215350  2d d4 65 b0 86 20 23 60 e0 56 97 ID 65b0 -22.0 35% seq e lowbat 1 RSSI 81']
    packet = TFA_1Packet.parse_text(None, lines)
    assert lines == []
    assert packet['dateTime'] == 1485215350
    assert packet['usUnits'] == weewx.METRIC
    assert packet['temperature.65B0.TFA_1Packet'] == -22
    assert packet['humidity.65B0.TFA_1Packet'] == 35
    assert packet['lowbat.65B0.TFA_1Packet'] == 1
    assert TFA_1Packet.parse_text(None, ['garbage']) == {}
