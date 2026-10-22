"""Run the upstream offline installation and CAP feed/report scenario."""

import os
import subprocess
import sys


def test_shipped_cap_feed_scenario(payload):
    result = subprocess.run([sys.executable, str(payload / 'tests/smoke_test.py')],
        cwd=payload, env=dict(os.environ), capture_output=True, text=True, timeout=180)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'ok ' in result.stdout
