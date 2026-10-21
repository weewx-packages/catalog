"""Exercise legacy syntax and incomplete matrices without accepting false recovery."""

import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import issues
import source_quality as quality


def test_original_python2_source_fails_before_installation(tmp_path, monkeypatch):
    original = tmp_path / 'original'
    subprocess.run(['git', 'init', '-b', 'main', str(original)], check=True, capture_output=True)
    (original / 'install.py').write_text("print 'Python 2 only'\n")
    subprocess.run(['git', '-C', str(original), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(original), '-c', 'user.name=Test',
                    '-c', 'user.email=test@example.test', 'commit', '-m', 'Legacy installer'],
                   check=True, capture_output=True)
    commands = []

    def clone(args):
        commands.append(args)
        assert args[:2] == ['git', 'clone']
        subprocess.run(['git', 'clone', str(original), args[-1]], check=True, capture_output=True)

    monkeypatch.setattr(quality, 'command', clone)
    case, result = quality.check(dict(fork='org/legacy'), 'master', 'a' * 40, tmp_path / 'check')
    assert result['status'] == 'failed' and result['phase'] == 'syntax'
    assert 'Missing parentheses' in result['details'][0]
    assert case['source_sha'] != 'not-checked' and len(commands) == 1


def test_missing_development_job_cannot_close_a_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(quality, 'ROOT', tmp_path)
    (tmp_path / 'ci').mkdir()
    (tmp_path / 'ci/mirrors.json').write_text(json.dumps([
        dict(fork='org/extension', weekday=1, check='installation')]))
    folder = tmp_path / 'quality-1-master'
    result = folder / 'result-extension-master-3.14'
    result.mkdir(parents=True)
    case = dict(package='extension', branch='master', python='3.14')
    (folder / 'matrix.json').write_text(json.dumps(dict(weekday=1, include=[case])))
    (result / 'result.json').write_text('{"status":"passed"}')
    existing = dict(number=1, user={'login': 'github-actions[bot]'}, state='open',
                    body='<!-- weewx-compatibility:extension -->')
    monkeypatch.setattr(quality, 'github', Mock(return_value=[existing]))
    write = Mock()
    monkeypatch.setattr(issues, 'github', write)
    for key, value in dict(GITHUB_REPOSITORY='org/catalog', GITHUB_SERVER_URL='https://github.com',
                           GITHUB_RUN_ID='1').items():
        monkeypatch.setenv(key, value)
    quality.report(tmp_path)
    write.assert_not_called()


def test_relative_work_directory_and_station_failure(tmp_path, monkeypatch):
    """Use a real Git archive, then refuse to blame the extension for station setup."""
    monkeypatch.chdir(tmp_path)
    original = tmp_path / 'original'
    subprocess.run(['git', 'init', '-b', 'main', str(original)], check=True, capture_output=True)
    (original / 'install.py').write_text('VERSION = "1.0"\n')
    subprocess.run(['git', '-C', str(original), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(original), '-c', 'user.name=Test',
                    '-c', 'user.email=test@example.test', 'commit', '-m', 'Installer'],
                   check=True, capture_output=True)

    def command(args, **kwargs):
        if args[:2] == ['git', 'clone']:
            args = ['git', 'clone', str(original), args[-1]]
        if args[0] == 'weectl':
            assert (tmp_path / 'relative/package.zip').is_file()
            raise subprocess.CalledProcessError(1, args)
        subprocess.run(args, check=True, capture_output=True)

    monkeypatch.setattr(quality, 'command', command)
    _, result = quality.check(dict(fork='org/extension'), 'master', 'a' * 40, Path('relative'))
    assert result['status'] == 'error' and result['phase'] == 'station setup'
