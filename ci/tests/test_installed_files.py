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
