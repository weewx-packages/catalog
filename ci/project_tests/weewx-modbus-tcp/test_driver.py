"""Check Modbus register word order and reject incomplete 32-bit values."""

import pytest
from user.ModbusTcp import ModbusTcpDriver


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/ModbusTcp.py').read_bytes() == (payload / 'bin/user/ModbusTcp.py').read_bytes()


def test_holding_register_word_order_and_short_reply():
    driver = ModbusTcpDriver.__new__(ModbusTcpDriver)
    assert driver._convert_value([0x1234, 0xabcd], {'index': 0, 'data_type': 'int32'}) == 0x1234abcd
    assert driver._convert_value([0, 250], {'index': 1, 'data_type': 'int16'}) == 250
    with pytest.raises(IndexError, match='requires two registers'):
        driver._convert_value([0xffff], {'index': 0, 'data_type': 'int32'})
