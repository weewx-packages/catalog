"""Reject importable installer substitutions even when the payload suite passes."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from installed_files import changed_files


def test_installer_cannot_replace_runtime_with_importable_stub(tmp_path):
    source = tmp_path / 'payload/notify.py'
    installed = tmp_path / 'station/notify.py'
    source.parent.mkdir()
    installed.parent.mkdir()
    source.write_text('class NotifyThread:\n    pass\n')
    installed.write_text('# Import works, but the notification thread is gone.\n')
    assert changed_files([(str(source), str(installed))]) == [str(installed)]
    installed.write_bytes(source.read_bytes())
    assert changed_files([(str(source), str(installed))]) == []
    installed.unlink()
    assert changed_files([(str(source), str(installed))]) == [str(installed)]


def test_repository_paths_reject_root_files_and_top_level_bin_packages(tmp_path):
    from installed_files import unsupported_paths

    paths = [('source', str(tmp_path / name)) for name in (
        'bin/user/driver.py', 'skins/Skin/index.html.tmpl', 'bin/airq_conf',
        'bin/schemas/driver.py', 'bin/weewx_sqm_le/service.py', 'openweather_fields.yaml')]
    assert unsupported_paths(paths, tmp_path) == [destination for _, destination in paths[2:]]


def test_cli_verifier_rejects_a_forbidden_non_python_destination(tmp_path):
    import os
    import subprocess

    fake_core = tmp_path / 'core/weecfg'
    fake_core.mkdir(parents=True)
    (fake_core / '__init__.py').write_text(
        "def get_extension_installer(path):\n    return path, {'files': []}\n")
    (fake_core / 'extension.py').write_text('''from pathlib import Path
class ExtensionEngine:
    @staticmethod
    def _gen_file_paths(station, payload, files):
        return [(str(Path(payload) / 'fields.yaml'), str(Path(station) / 'fields.yaml'))]
''')
    checker = Path(__file__).resolve().parents[1] / 'installed_files.py'
    result = subprocess.run([sys.executable, str(checker), str(tmp_path / 'payload'),
                             str(tmp_path / 'station')], text=True, capture_output=True,
                            env=dict(os.environ, PYTHONPATH=str(fake_core.parent)))
    assert result.returncode != 0
    assert 'Destinations outside repository-managed roots' in result.stderr
