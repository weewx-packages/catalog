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
