"""Restore real wiki histories and keep verified backups after remote failures."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import wiki_backup as wiki


def commit(directory, message):
    """Commit the fixture with a distinct author whose metadata must survive."""
    wiki.git(['-C', str(directory), 'add', '--all'])
    wiki.git(['-C', str(directory), '-c', 'user.name=Wiki fixture author',
              '-c', 'user.email=wiki@example.test', 'commit', '-m', message])


@pytest.fixture
def source(tmp_path):
    directory = tmp_path / 'wiki'
    wiki.git(['init', '-b', 'main', str(directory)])
    (directory / 'Home.md').write_text('Private wiki body in its first revision.\n')
    (directory / 'image.bin').write_bytes(bytes(range(256)))
    commit(directory, 'Original page')
    wiki.git(['-C', str(directory), 'tag', 'original'])
    (directory / 'Home.md').unlink()
    (directory / 'Current.md').write_text('The original page was removed.\n')
    commit(directory, 'Remove original page')
    wiki.git(['-C', str(directory), 'branch', 'notes'])
    return directory


def test_bundle_restores_deleted_pages_binary_files_authors_and_all_refs(source, tmp_path):
    target = dict(url=source.as_uri(), enabled=True)
    backup = tmp_path / 'backup'
    record = wiki.capture_wiki('owner/project', target, backup, {})
    assert record['status'] == 'saved'
    bundle = backup / record['backup']['path']
    restored = tmp_path / 'restored'
    wiki.git(['clone', '--mirror', str(bundle), str(restored)])
    assert wiki.refs(restored) == wiki.refs(source)
    assert wiki.git(['-C', str(restored), 'show', 'original:Home.md']) == 'Private wiki body in its first revision.\n'
    assert wiki.git(['-C', str(restored), 'log', '-1', '--format=%an']) == 'Wiki fixture author\n'
    binary = subprocess.check_output(['git', '-C', str(restored), 'show', 'main:image.bin'])
    assert binary == bytes(range(256))
    before = bundle.read_bytes()
    again = wiki.capture_wiki('owner/project', target, backup, record)
    assert again['status'] == 'saved' and again['backup']['sha256'] == record['backup']['sha256']
    assert bundle.read_bytes() == before


@pytest.mark.parametrize('failure', ['unavailable', 'disabled', 'empty'])
def test_failure_retains_last_bundle_and_reports_it_without_publishing_content(source, tmp_path, monkeypatch, failure):
    backup = tmp_path / 'backup'
    backup.mkdir()
    target = dict(url=source.as_uri(), enabled=True)
    monkeypatch.setattr(wiki, 'targets', lambda *args: {'owner/project': target})
    output = tmp_path / 'public.json'
    assert wiki.capture([], 1, backup, output) == 0
    previous = json.loads((backup / 'wiki-index.json').read_text())['owner/project']
    bundle = backup / previous['backup']['path']
    before = bundle.read_bytes()
    if failure == 'unavailable':
        target['url'] = (tmp_path / 'missing.wiki.git').as_uri()
    elif failure == 'disabled':
        target['enabled'] = False
    else:
        empty = tmp_path / 'empty.git'
        wiki.git(['init', '--bare', str(empty)])
        target['url'] = empty.as_uri()
    assert wiki.capture([], 1, backup, output) == 1
    record = json.loads((backup / 'wiki-index.json').read_text())['owner/project']
    assert record['status'] == failure
    assert record['backup'] == previous['backup'] and bundle.read_bytes() == before
    public = json.loads(output.read_text())['wikis']['owner/project']
    assert public['retained'] and public['last_verified'] == previous['backup']['verified_at']
    assert 'Private wiki body' not in output.read_text()
    assert 'error' not in public and 'refs' not in public


def test_restore_failure_cannot_replace_a_good_bundle(source, tmp_path, monkeypatch):
    backup = tmp_path / 'backup'
    target = dict(url=source.as_uri(), enabled=True)
    previous = wiki.capture_wiki('owner/project', target, backup, {})
    bundle = backup / previous['backup']['path']
    before = bundle.read_bytes()
    (source / 'Current.md').write_text('New upstream revision.\n')
    commit(source, 'Update wiki')
    real_git = wiki.git

    def fail_validation(arguments):
        if arguments[-2:] == ['fsck', '--full']:
            raise subprocess.CalledProcessError(1, arguments, stderr='restored object is corrupt')
        return real_git(arguments)

    monkeypatch.setattr(wiki, 'git', fail_validation)
    result = wiki.capture_wiki('owner/project', target, backup, previous)
    assert result['status'] == 'unavailable'
    assert result['error'] == 'restored object is corrupt'
    assert result['backup'] == previous['backup'] and bundle.read_bytes() == before


def test_disappearing_discovery_entry_keeps_its_backup_under_observation(source, tmp_path, monkeypatch):
    backup = tmp_path / 'backup'
    backup.mkdir()
    output = tmp_path / 'summary.json'
    monkeypatch.setattr(wiki, 'targets', lambda *args: {
        'owner/project': dict(url=source.as_uri(), enabled=True)})
    assert wiki.capture([], 1, backup, output) == 0
    monkeypatch.setattr(wiki, 'targets', lambda *args: {})
    assert wiki.capture([], 1, backup, output) == 0
    source.rename(tmp_path / 'removed-upstream')
    assert wiki.capture([], 1, backup, output) == 1
    record = json.loads(output.read_text())['wikis']['owner/project']
    assert record['status'] == 'unavailable' and record['retained']


def test_gitlab_disabled_wiki_is_not_treated_as_an_authentication_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(wiki, 'get', lambda url: {'data': {'project': {'wikiEnabled': False}}})
    result = wiki.capture_wiki('gitlab.com/group/project', dict(
        url='https://gitlab.com/group/project.wiki.git', enabled=None), tmp_path, {})
    assert result['status'] == 'disabled' and 'backup' not in result


@pytest.mark.parametrize('repository', ['../escape', 'owner/../escape', 'owner//project', 'owner/\\escape'])
def test_repository_names_cannot_escape_backup_directory(repository):
    with pytest.raises(ValueError, match='Invalid wiki repository'):
        wiki.wiki_url(repository)


def test_discovery_covers_upstreams_own_wikis_core_and_pagination(monkeypatch):
    entries = [dict(fork='weewx-packages/extension', upstream='https://github.com/author/extension.git', weekday=2)]
    repositories = [dict(full_name='weewx-packages/extension', has_wiki=True, fork=True)]
    repositories += [dict(full_name='weewx-packages/extra-%s' % n, has_wiki=True, fork=False) for n in range(99)]
    repositories += [dict(full_name='weewx-packages/weewx', has_wiki=True, fork=True)]
    calls = []

    def api(path):
        calls.append(path)
        if path == 'repos/weewx-packages/weewx':
            return dict(parent=dict(full_name='weewx/weewx', has_wiki=True))
        page = int(path.rsplit('=', 1)[1])
        return repositories[(page - 1) * 100:page * 100]

    monkeypatch.setattr(wiki, 'github', api)
    groups = [wiki.targets(entries, weekday) for weekday in range(1, 6)]
    names = [name for group in groups for name in group]
    assert len(names) == len(set(names)) == 103
    assert {'author/extension', 'weewx-packages/extension'} <= groups[1].keys()
    assert {'weewx/weewx', 'weewx-packages/weewx'} <= set(names)
    assert any(path.endswith('page=2') for path in calls)


def test_git_cannot_wait_for_terminal_credentials(monkeypatch):
    seen = {}

    def run(arguments, **options):
        seen.update(options)
        assert 'credential.https://github.com.helper=!gh auth git-credential' in arguments
        return subprocess.CompletedProcess(arguments, 0, '', '')

    monkeypatch.setattr(wiki.subprocess, 'run', run)
    wiki.git(['ls-remote', 'https://github.com/owner/project.wiki.git'])
    assert seen['env']['GIT_TERMINAL_PROMPT'] == '0'
