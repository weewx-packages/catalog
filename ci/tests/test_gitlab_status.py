"""Keep GitLab discussion pagination and issue/MR numbering distinct."""

import json
from pathlib import Path
import sys
from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gitlab_status as gitlab
from upstream_status import index


def test_notes_follow_cursor_and_preserve_edits(monkeypatch):
    responses = [dict(data=dict(project=dict(issue=dict(notes=dict(
        nodes=[dict(body=body, updatedAt='now')],
        pageInfo=dict(hasNextPage=more, endCursor='next'))))))
        for body, more in (('First reply', True), ('Edited reply', False))]
    get = Mock(side_effect=responses)
    monkeypatch.setattr(gitlab, 'get', get)
    assert len(gitlab.notes('owner/project', 'issue', 1)) == 2
    query = parse_qs(urlparse(get.call_args.args[0]).query)['query'][0]
    assert 'after:"next"' in query and 'updatedAt' in query


def test_issue_and_merge_request_with_same_number_do_not_collide(monkeypatch):
    def pages(url):
        if '/repository/tree' in url:
            return [dict(type='blob', path='COPYING', id='hash')]
        if url.endswith('/diffs'):
            return [dict(diff='Private patch')]
        return [dict(iid=1, title='Report', web_url='https://gitlab.com/item')]

    monkeypatch.setattr(gitlab, 'pages', pages)
    monkeypatch.setattr(gitlab, 'get', Mock(return_value={}))
    monkeypatch.setattr(gitlab, 'notes', Mock(return_value=[dict(body='Private reply')]))
    snapshot = gitlab.collect('owner/project')
    public = index(snapshot)
    assert set(public['items']) == {'1', '!1'}
    assert public['items']['!1']['kind'] == 'PR'
    assert public['notices'] == {'COPYING': 'hash'}
    assert 'Private' not in json.dumps(public)
