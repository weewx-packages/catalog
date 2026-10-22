"""Parse nested IP100 XML hardware and weather measurements."""

from user.ip100 import IP100Station


def test_installed_payload(payload, station):
    """Require the installed runtime files to match the verified archive bytes."""
    assert (station / 'bin/user/ip100.py').read_bytes() == (payload / 'bin/user/ip100.py').read_bytes()


def test_nested_xml_numeric_fields_and_malformed_packet():
    wire = b'<status><hardware><device><model>IP100</model></device></hardware><weather><temperature><current>-3.5</current></temperature><wind><speed>0</speed><direction>270</direction><gust_speed>12.5</gust_speed><gust_direction>315</gust_direction></wind></weather></status>'
    assert IP100Station.parse_data(wire) == {
        'model': 'IP100', 'temperature': -3.5, 'wind_speed': 0.0,
        'wind_dir': 270.0, 'gust_speed': 12.5, 'gust_dir': 315.0}
    assert IP100Station.parse_data(b'<status') == {}
