"""Read public GitLab trackers without requiring an account or a write token."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import urlopen


def get(url):
    """Return a public JSON response.

    Args:
        url (str): Complete GitLab API URL.

    Returns:
        dict|list: Decoded response.
    """
    with urlopen(url, timeout=60) as response:
        return json.load(response)


def pages(url):
    """Collect a REST array across every page.

    Args:
        url (str): Endpoint, possibly with query parameters.

    Returns:
        list[dict]: All returned records.
    """
    records = []
    page = 1
    while True:
        batch = get(url + ('&' if '?' in url else '?') + 'per_page=100&page=%s' % page)
        if not isinstance(batch, list):
            raise ValueError('Expected a GitLab array')
        records.extend(batch)
        if len(batch) < 100:
            return records
        page += 1


def notes(repository, kind, number):
    """Read all notes through GraphQL, including anonymous public discussions.

    Args:
        repository (str): GitLab namespace/project.
        kind (str): GraphQL issue or mergeRequest field.
        number (int): Project-local issue or merge request number.

    Returns:
        list[dict]: Notes, including system records and author metadata.
    """
    records, cursor = [], None
    # The public REST notes endpoints can require authentication even when the
    # same discussion is publicly readable through GraphQL.
    while True:
        query = ('{project(fullPath:%s){%s(iid:%s){notes(first:100,after:%s)'
                 '{nodes{id body createdAt updatedAt system author{username}}'
                 'pageInfo{hasNextPage endCursor}}}}}' %
                 (json.dumps(repository), kind, json.dumps(str(number)), json.dumps(cursor)))
        result = get('https://gitlab.com/api/graphql?' + urlencode({'query': query}))
        if not isinstance(result, dict):
            raise ValueError('Expected a GitLab GraphQL object')
        if result.get('errors'):
            raise ValueError('GitLab notes query failed: %s' % result['errors'])
        connection = result['data']['project'][kind]['notes']
        records.extend(connection['nodes'])
        if not connection['pageInfo']['hasNextPage']:
            return records
        cursor = connection['pageInfo']['endCursor']


def collect(repository):
    """Capture open GitLab issues, merge requests, notes and available file diffs.

    Args:
        repository (str): GitLab namespace/project.

    Returns:
        dict: Private snapshot using the shared activity index format.
    """
    prefix = 'https://gitlab.com/api/v4/projects/' + quote(repository, safe='')
    metadata = get(prefix)
    items = []
    for endpoint, field in (('issues', 'issue'), ('merge_requests', 'mergeRequest')):
        for item in pages(prefix + '/' + endpoint + '?state=opened'):
            item['discussion'] = notes(repository, field, item['iid'])
            item.update(number=str(item['iid']), html_url=item['web_url'])
            if field == 'mergeRequest':
                item.update(number='!' + str(item['iid']), pull_request={})
                item['details'] = get(prefix + '/merge_requests/' + str(item['iid']))
                item['files'] = pages(prefix + '/merge_requests/' + str(item['iid']) + '/diffs')
            items.append(item)
    tree = pages(prefix + '/repository/tree?recursive=true')
    notices = {item['path']: item['id'] for item in tree if item['type'] == 'blob'
               and any(term in Path(item['path']).name.lower()
                       for term in ('license', 'licence', 'copying', 'notice', 'read this', 'ofl'))}
    return dict(repository='gitlab.com/' + repository,
                captured_at=datetime.now(timezone.utc).isoformat(), metadata=metadata,
                open_items=items, notices=notices, notice_scan_complete=True)
