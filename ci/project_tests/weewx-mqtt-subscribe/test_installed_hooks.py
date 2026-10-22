"""Resolve installed service classes in a process whose imports use only the station."""
import os
import subprocess
import sys


SCRIPT = r"""
import inspect
from pathlib import Path
import sys
import weecfg
from weeutil.weeutil import get_object, option_as_list
station = Path(sys.argv[1])
_, config = weecfg.read_config(str(station / 'weewx.conf'))
for services in config['Engine']['Services'].values():
    for name in option_as_list(services):
        if name.startswith('user.'):
            service = get_object(name)
            assert callable(service), name
            assert Path(inspect.getfile(service)).is_relative_to(station / 'bin'), name
"""


def test_installed_service_hooks(station):
    result = subprocess.run([sys.executable, '-c', SCRIPT, str(station)], cwd=station,
                            env=dict(os.environ, PYTHONPATH=str(station / 'bin')),
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
