"""Preserve discussion changes and avoid confusing a first capture with closures."""

import copy
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import upstream_status as status


def test_api_collects_all_pages(monkeypatch):
    run = Mock(return_value=subprocess.CompletedProcess([], 0, '[[{"number":1}],[{"number":2}]]', ''))
    monkeypatch.setattr(status.subprocess, 'run', run)
    assert status.api('repos/owner/repo/issues', paginate=True) == [{'number': 1}, {'number': 2}]
    assert '--paginate' in run.call_args.args[0]


def test_comment_edits_and_closures_survive_summary_without_public_bodies():
    snapshot = dict(captured_at='now', notices={'LICENSE': 'one'}, notice_scan_complete=True,
                    open_items=[dict(number=1, title='A report', html_url='https://issue/1',
                                     discussion=[dict(body='original discussion')])])
    before = status.index(snapshot)
    assert 'original discussion' not in json.dumps(before)
    changed = copy.deepcopy(snapshot)
    changed['open_items'][0]['discussion'][0]['body'] = 'edited discussion'
    changed['notices']['LICENSE'] = 'two'
    delta = status.changes(before, status.index(changed))
    assert len(delta['changed']) == 1 and delta['license_notices_changed']
    assert not delta['new'] and not delta['closed']
    changed['open_items'] = []
    assert len(status.changes(before, status.index(changed))['closed']) == 1
    initial = status.changes(None, before)
    assert initial['initial'] and not initial['closed']


def test_missing_capture_cannot_publish_an_empty_status_issue(tmp_path, monkeypatch):
    api = Mock()
    monkeypatch.setattr(status, 'api', api)
    with pytest.raises(ValueError, match='No complete'):
        status.report(tmp_path, 'org/catalog', 'https://run')
    api.assert_not_called()


def test_wiki_reporting_keeps_content_private_and_does_not_notify_on_timestamp_only_changes(tmp_path, monkeypatch):
    monkeypatch.setattr(status, 'ROOT', tmp_path)
    (tmp_path / 'ci').mkdir()
    group = tmp_path / 'activity-1'
    group.mkdir()
    (group / 'activity.json').write_text(json.dumps(dict(repositories={
        'owner/project': dict(captured_at='now', items={}, notices={}, notice_scan_complete=True)},
        activity={})))
    record = dict(url='https://github.com/owner/project.wiki.git', status='saved',
                  checked_at='2026-10-22', last_verified='2026-10-22', retained=False, digest='one')
    path = group / 'wiki-activity.json'
    path.write_text(json.dumps(dict(wikis={'owner/project': record})))
    issue = dict(number=1, body=status.MARKER, user={'login': 'github-actions[bot]'})
    api = Mock(side_effect=lambda endpoint, *args, **kwargs: [issue] if '?' in endpoint else issue)
    monkeypatch.setattr(status, 'api', api)
    status.report(tmp_path, 'org/catalog', 'https://run')
    assert any('/comments' in call.args[0] for call in api.call_args_list)
    assert '| Wiki | Status |' in api.call_args_list[1].args[1]['body']
    api.reset_mock()
    record['checked_at'] = record['last_verified'] = '2026-10-29'
    path.write_text(json.dumps(dict(wikis={'owner/project': record})))
    status.report(tmp_path, 'org/catalog', 'https://run')
    assert not any('/comments' in call.args[0] for call in api.call_args_list)
    api.reset_mock()
    record.update(status='unavailable', retained=True)
    path.write_text(json.dumps(dict(wikis={'owner/project': record})))
    status.report(tmp_path, 'org/catalog', 'https://run')
    assert 'last backup retained' in api.call_args_list[-1].args[1]['body']
