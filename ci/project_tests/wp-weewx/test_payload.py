"""Install the plugin tree and test PHP data handling through local WordPress API fixtures."""

import json
from pathlib import Path
import shutil
import subprocess


def test_php_fetch_parse_cache_and_temperature(payload, tmp_path):
    # Install the exact archive tree into the normal WordPress plugin directory.
    plugin = tmp_path / 'wp-content/plugins/wp-weewx'
    shutil.copytree(payload, plugin)
    fixture = Path(__file__).with_name('fixture.php')
    run = subprocess.run(['php', str(fixture), str(plugin)], text=True,
                         capture_output=True, check=True)
    result = json.loads(run.stdout)
    assert result == {'zero': 0, 'missing': None, 'array': [1, None, 3],
                      'temperature': '20.00 C', 'cached': True, 'stale': True,
                      'warning': 'Unexpected HTTP status: 503', 'requests': 2}
    for source in plugin.rglob('*.php'):
        subprocess.run(['php', '-l', str(source)], capture_output=True, check=True)
