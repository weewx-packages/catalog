"""Keep weekday groups and mirror credentials separate from upstream code."""

import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mirrors


def test_weekly_selection_and_manual_run():
    entries = [dict(weekday=day) for day in (1, 1, 3, 5)]
    assert mirrors.matrix(entries, '43 3 * * 3') == {'include': [{'weekday': 3}]}
    assert mirrors.matrix(entries, '43 3 * * 2') == {'include': []}
    assert mirrors.matrix(entries, '') == {'include': [{'weekday': day} for day in (1, 3, 5)]}
    with pytest.raises(ValueError, match='Monday through Friday'):
        mirrors.matrix([dict(weekday=7)], '')


def test_source_jobs_only_cover_weekdays_with_raw_installation_checks():
    entries = [dict(weekday=1, check='catalog'), dict(weekday=2, check='installation'),
               dict(weekday=3, check='component'), dict(weekday=4, check='external')]
    assert mirrors.check_matrix(entries, '') == {'include': [
        dict(weekday=2, branch=branch) for branch in ('master', 'development')]}
    assert mirrors.check_matrix(entries, '43 3 * * 1') == {'include': []}
    assert mirrors.matrix(entries, '') == {'include': [dict(weekday=day) for day in range(1, 5)]}


def test_current_registry_routes_checks_to_the_project_workflow():
    root = Path(__file__).resolve().parents[2]
    entries = json.loads((root / 'ci/mirrors.json').read_text())
    assert mirrors.check_matrix(entries, '') == {'include': []}
    workflow = (root / '.github/workflows/mirrors.yml').read_text()
    assert 'python3 ci/mirrors.py checks --schedule' in workflow
    assert "needs.select.outputs.check_count != '0'" in workflow


def test_one_job_per_mirror_with_its_own_secret():
    entries = [dict(weekday=1, fork='weewx-packages/weewx-gw1000'),
               dict(weekday=1, fork='weewx-packages/continuation', sync=False),
               dict(weekday=3, fork='weewx-packages/weewx-NovaSDS011')]
    assert mirrors.repositories(entries, '43 3 * * 1') == {'include': [
        dict(weekday=1, fork='weewx-packages/weewx-gw1000', secret='MIRROR_KEY_WEEWX_GW1000')]}
    assert [item['secret'] for item in mirrors.repositories(entries, '')['include']] == [
        'MIRROR_KEY_WEEWX_GW1000', 'MIRROR_KEY_WEEWX_NOVASDS011']
    with pytest.raises(ValueError, match='share a secret name'):
        mirrors.repositories([dict(weekday=1, fork='weewx-packages/a-b'),
                              dict(weekday=2, fork='weewx-packages/a_b')], '')


def test_current_registry_has_distinct_secrets_and_workflow_reads_one():
    root = Path(__file__).resolve().parents[2]
    entries = json.loads((root / 'ci/mirrors.json').read_text())
    selected = mirrors.repositories(entries, '')['include']
    assert len(selected) == sum(1 for entry in entries if entry.get('sync', True))
    workflow = (root / '.github/workflows/mirrors.yml').read_text()
    assert 'MIRROR_SSH_KEY: ${{ secrets[matrix.secret] }}' in workflow
    assert 'name: mirrors-${{ matrix.weekday }}' in workflow
    assert 'deployment: false' in workflow


def test_sync_passes_only_the_key_path_to_git(monkeypatch):
    entries = [dict(weekday=1, fork='weewx-packages/working',
                    upstream='https://github.com/author/working.git')]
    seen = []

    def git(args, env):
        assert 'MIRROR_SSH_KEY' not in env
        key_path = Path(env['GIT_SSH_COMMAND'].split()[2])
        assert key_path.stat().st_mode & 0o777 == 0o600
        seen.append((args[-1], key_path.read_text()))
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(mirrors.subprocess, 'check_output', lambda *args, **kwargs:
                        json.dumps({'ssh_keys': ['ssh-ed25519 github-host-key']}))
    monkeypatch.setattr(mirrors.subprocess, 'run', git)
    with patch.dict(os.environ, MIRROR_SSH_KEY='working-private-key'):
        assert mirrors.sync(entries, 'weewx-packages/working', 'working-private-key')
    assert seen == [('git@github.com:weewx-packages/working.git', 'working-private-key\n')]


def test_missing_secret_fails_without_pushing(monkeypatch):
    push = Mock()
    monkeypatch.setattr(mirrors.subprocess, 'run', push)
    assert not mirrors.sync([dict(weekday=1, fork='weewx-packages/missing')],
                            'weewx-packages/missing', '')
    push.assert_not_called()


def test_mirror_cannot_push_outside_the_organization():
    with pytest.raises(ValueError, match='weewx-packages'):
        mirrors.sync([dict(weekday=1, fork='author/original')], 'author/original', 'key')
    with pytest.raises(ValueError, match='not listed'):
        mirrors.sync([], 'weewx-packages/unknown', 'key')


def test_independent_continuation_cannot_be_overwritten(monkeypatch):
    push = Mock()
    monkeypatch.setattr(mirrors.subprocess, 'run', push)
    assert mirrors.sync([dict(weekday=1, fork='weewx-packages/continuation', sync=False)],
                        'weewx-packages/continuation', 'unused-key')
    push.assert_not_called()
