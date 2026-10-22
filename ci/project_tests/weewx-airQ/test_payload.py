"""Decrypt device replies and convert real air-Q observation fields."""

import base64
import json
from types import SimpleNamespace
from Cryptodome.Cipher import AES
import pytest
import weewx
from user import airQ_corant as airq


def test_encrypted_reply_and_plain_error():
    clear = json.dumps({'temperature': [0, 0.1], 'co2': [514, 2]}).encode()
    padding = 16 - len(clear) % 16
    iv = bytes(range(16))
    cipher = AES.new(b'fixture'.ljust(32, b'0'), AES.MODE_CBC, iv)
    encoded = base64.b64encode(iv + cipher.encrypt(clear + bytes([padding]) * padding))
    reply = airq.airQreply(json.dumps({'content': encoded.decode()}), 'fixture')
    assert reply['content'] == {'temperature': [0, 0.1], 'co2': [514, 2]}
    assert airq.airQreply('{"error":"denied"}', 'fixture') == {'error': 'denied'}


def test_temperature_zero_and_particle_mapping():
    service = airq.AirqService(SimpleNamespace(bind=lambda *args: None), {})
    converted = service.airq_to_weewx({'temperature': 0, 'co2': 514,
                                    'pm2_5': 12.5}, None, weewx.US)
    assert converted['airqTemp'] == pytest.approx(32)
    assert converted['co2'] == 514
    assert converted['pm2_5'] == 12.5
