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


def test_failed_mirror_does_not_skip_other_repositories(monkeypatch):
    entries = [dict(weekday=day, fork='weewx-packages/' + name,
                    upstream='https://github.com/author/' + name + '.git')
               for day, name in ((1, 'broken'), (1, 'missing'), (1, 'working'), (3, 'other'))]
    keys = {'weewx-packages/' + name: name + '-private-key' for name in ('broken', 'working')}
    seen = []

    def git(args, env):
        assert 'MIRROR_SSH_KEYS' not in env
        key_path = Path(env['GIT_SSH_COMMAND'].split()[2])
        assert key_path.stat().st_mode & 0o777 == 0o600
        seen.append((args[-1], key_path.read_text()))
        return subprocess.CompletedProcess(args, 1 if 'broken' in args[-1] else 0)

    monkeypatch.setattr(mirrors.subprocess, 'check_output', lambda *args, **kwargs:
                        json.dumps({'ssh_keys': ['ssh-ed25519 github-host-key']}))
    monkeypatch.setattr(mirrors.subprocess, 'run', git)
    with patch.dict(os.environ, MIRROR_SSH_KEYS=json.dumps(keys)):
        failed = mirrors.sync(entries, 1, keys)
    assert failed == ['weewx-packages/broken', 'weewx-packages/missing']
    assert seen == [('git@github.com:weewx-packages/broken.git', 'broken-private-key'),
                    ('git@github.com:weewx-packages/working.git', 'working-private-key')]


def test_mirror_cannot_push_outside_the_organization(monkeypatch):
    monkeypatch.setattr(mirrors.subprocess, 'check_output', lambda *args, **kwargs:
                        json.dumps({'ssh_keys': []}))
    with pytest.raises(ValueError, match='weewx-packages'):
        mirrors.sync([dict(weekday=1, fork='author/original')], 1, {})


def test_independent_continuation_cannot_be_overwritten(monkeypatch):
    monkeypatch.setattr(mirrors.subprocess, 'check_output', lambda *args, **kwargs:
                        json.dumps({'ssh_keys': []}))
    push = Mock()
    monkeypatch.setattr(mirrors.subprocess, 'run', push)
    assert mirrors.sync([dict(weekday=1, fork='weewx-packages/continuation', sync=False)],
                        1, {'weewx-packages/continuation': 'unused-key'}) == []
    push.assert_not_called()
