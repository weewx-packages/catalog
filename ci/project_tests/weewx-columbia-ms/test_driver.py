"""Parse MicroServer XML measurements, unit groups and truncated messages."""

import pytest
import weewx
from user.columbia_ms import ColumbiaMicroServerStation as Station


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/columbia_ms.py').read_bytes() == (payload / 'bin/user/columbia_ms.py').read_bytes()


def test_xml_measurements_group_units_and_truncated_end():
    xml = ('<oriondata><meas name="mtTemp1" unit="C">-2.5</meas>'
           '<meas name="mtWindSpeed" unit="m/s">3.2</meas>'
           '<meas name="mtRelHumidity" unit="%">0</meas></oriondata>')
    data = Station.parse_data(xml)
    assert data['temp']['mtTemp1'] == -2.5
    assert data['temp']['base_units'] == 'C'
    assert data['wind']['mtWindSpeed'] == 3.2
    assert data['generic']['mtRelHumidity'] == 0
    assert Station.parse_data(xml.replace('</oriondata>', '</ori\x00')) == data
    with pytest.raises(weewx.WeeWxIOError):
        Station.parse_data('<wrong><meas/></wrong>')
