"""Check RTSP commands and use real ffmpeg to capture a local image fixture."""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from PIL import Image


def test_bundled_protocol_regressions(payload, station, tmp_path):
    report = tmp_path / 'upstream.xml'
    env = dict(os.environ, PYTHONPATH=':'.join(map(str, [payload / 'bin', station / 'bin', payload / 'bin/user/tests/unit', payload / 'tests'])))
    command = 'import sys,user,pytest; user.__path__.insert(0,sys.argv[1]); raise SystemExit(pytest.main(sys.argv[2:]))'
    run = subprocess.run([sys.executable, '-c', command, str(payload / 'bin/user'),
                          '-q', 'tests/test_rtspimage.py', '--junitxml=' + str(report)],
                         cwd=payload, env=env, text=True, capture_output=True, timeout=180)
    assert run.returncode == 0, run.stdout + run.stderr
    cases = ET.parse(report).findall('.//testcase')
    assert len(cases) >= 26
    assert not any(case.find('skipped') is not None for case in cases)


def test_actual_ffmpeg_capture_from_local_frame(payload, station, tmp_path):
    spec = importlib.util.spec_from_file_location('fixture_rtspimage', payload / 'bin/user/rtspimage.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = tmp_path / 'fixture.png'
    Image.new('RGB', (24, 16), (255, 0, 0)).save(source)
    target = tmp_path / 'result.jpg'
    capture = module.RTSPCapture(name='fixture', url=str(source), destinations=[str(target)],
                                 rtsp_transport='')
    assert capture.capture() == [str(target)]
    with Image.open(target) as frame:
        assert frame.size == (24, 16)
        red, green, blue = frame.convert('RGB').getpixel((12, 8))
        assert red > 245 and green < 10 and blue < 10
