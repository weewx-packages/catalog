"""Generate the standalone SVG library and validate its XML and cloud symbols."""

import importlib.util
import subprocess
import sys
import xml.etree.ElementTree as ET


def test_generated_python_and_svg(payload, tmp_path):
    result = subprocess.run([sys.executable, str(payload / 'bin/icons.py'), '--write-py'],
                            cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    generated = tmp_path / 'generated_icons.py'
    generated.write_text(result.stdout)
    spec = importlib.util.spec_from_file_location('generated_icons', generated)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sunny = ET.fromstring(module.svg_icon_n(0, width=256))
    cloudy = ET.fromstring(module.svg_icon_n(8, width=256))
    assert sunny.attrib['width'] == '256'
    assert sunny.attrib['height'] == '200.0'
    assert len(sunny.findall('.//{http://www.w3.org/2000/svg}circle')) > 0
    assert ET.tostring(sunny) != ET.tostring(cloudy)
    rainy = ET.fromstring(module.svg_icon_ww(63))
    assert rainy.findall('.//{http://www.w3.org/2000/svg}path')

    assert module.svg_icon_ww(999) == ''
