"""Decode an ASN.1 reply through the synchronous SNMP record path."""

import queue
import threading
from unittest.mock import Mock
from pyasn1.codec.ber import decoder
from pysnmp.proto.rfc1902 import Integer
from user import snmp


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/snmp.py').read_bytes() == (payload / 'bin/user/snmp.py').read_bytes()


def test_asn1_integer_reply_conversion_and_unit_group(monkeypatch):
    thread = snmp.SNMPthread.__new__(snmp.SNMPthread)
    threading.Thread.__init__(thread, name='fixture')
    thread.data_queue = queue.Queue()
    thread.conf_dict = {'protocol_version': '2c', 'community': 'public-fixture',
                        'host': '192.0.2.1', 'port': 161,
                        'loop': [{'name': 'voltage', 'unit': 'volt', 'group': 'group_volt', 'conversion': lambda value: value / 100}]}
    thread.mpModel = 1
    identity = Mock()
    identity.getOid.return_value = (1,3,6,1,4,1,999,1,0)
    thread.ot = {'loop': [(identity,)]}
    value, remaining = decoder.decode(bytes.fromhex('020204e2'), asn1Spec=Integer())
    assert remaining == b''
    monkeypatch.setattr(snmp, 'getCmd', lambda *args: iter([(None, 0, 0, [(identity, value)])]))
    thread.getRecord('loop')
    name, actual = thread.data_queue.get_nowait()
    assert name == 'fixture'
    assert actual['voltage'].value == 12.5
    assert actual['voltage'].unit == 'volt'
    assert actual['voltage'].group == 'group_volt'
