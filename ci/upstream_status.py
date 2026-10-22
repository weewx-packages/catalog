"""Back up open upstream discussions and report changes without running extensions."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

from gitlab_status import collect as collect_gitlab

ROOT = Path(__file__).resolve().parents[1]
MARKER = '<!-- weewx-upstream-activity -->'


def api(path, data=None, method=None, paginate=False):
    """Read public upstream data or update the catalog's activity issue.

    Args:
        path (str): GitHub API path.
        data (dict|None): Optional JSON request body.
        method (str|None): HTTP method, or gh's default.
        paginate (bool): Collect every page of an array response.

    Returns:
        dict|list: Decoded object or complete array.
    """
    args = ['gh', 'api', path]
    if paginate:
        args.extend(['--paginate', '--slurp'])
    if method:
        args.extend(['--method', method])
    if data is not None:
        args.extend(['--input', '-'])
    result = subprocess.run(args, input=json.dumps(data) if data is not None else None,
                            text=True, capture_output=True, check=True, timeout=120)
    decoded = json.loads(result.stdout)
    return [item for page in decoded for item in page] if paginate else decoded


def collect(repository):
    """Capture open issues and PRs, including discussions, reviews and file patches.

    Args:
        repository (str): GitHub owner/repository or gitlab.com/namespace/project.

    Returns:
        dict: Snapshot suitable for storage in the private backup repository.
    """
    if repository.startswith('gitlab.com/'):
        return collect_gitlab(repository.removeprefix('gitlab.com/'))
    prefix = 'repos/' + repository
    metadata = api(prefix)
    items = api(prefix + '/issues?state=open&per_page=100', paginate=True)
    if not isinstance(metadata, dict) or not isinstance(items, list):
        raise ValueError('Unexpected upstream repository or issue response')
    for item in items:
        number = str(item['number'])
        item['discussion'] = api(prefix + '/issues/' + number + '/comments?per_page=100', paginate=True)
        if 'pull_request' in item:
            item['pull_request_details'] = api(prefix + '/pulls/' + number)
            item['reviews'] = api(prefix + '/pulls/' + number + '/reviews?per_page=100', paginate=True)
            item['review_comments'] = api(prefix + '/pulls/' + number + '/comments?per_page=100', paginate=True)
            item['files'] = api(prefix + '/pulls/' + number + '/files?per_page=100', paginate=True)
    tree = api(prefix + '/git/trees/' + metadata['default_branch'] + '?recursive=1')
    if not isinstance(tree, dict):
        raise ValueError('Unexpected upstream tree response')
    notices = {item['path']: item['sha'] for item in tree['tree'] if item['type'] == 'blob'
               and any(term in Path(item['path']).name.lower()
                       for term in ('license', 'licence', 'copying', 'notice', 'read this', 'ofl'))}
    return dict(repository=repository, captured_at=datetime.now(timezone.utc).isoformat(),
                metadata=metadata, open_items=items, notices=notices,
                notice_scan_complete=not tree.get('truncated', False))


def index(snapshot):
    """Reduce a full backup to public activity metadata and content fingerprints.

    Args:
        snapshot (dict): Complete repository snapshot.

    Returns:
        dict: Summary excluding discussion bodies and file patches.
    """
    items = {}
    for item in snapshot['open_items']:
        items[str(item['number'])] = dict(title=item['title'], url=item['html_url'],
            kind='PR' if 'pull_request' in item else 'issue',
            digest=hashlib.sha256(json.dumps(item, sort_keys=True).encode()).hexdigest())
    return dict(captured_at=snapshot['captured_at'], items=items,
                notices=snapshot['notices'], notice_scan_complete=snapshot['notice_scan_complete'])


def changes(before, after):
    """Find newly open, changed, closed and license-notice changes in one capture.

    Args:
        before (dict|None): Previous repository index, or None for the first capture.
        after (dict): Current repository index.

    Returns:
        dict: Initial-capture flag and lists of public activity details.
    """
    previous = before['items'] if before else {}
    current = after['items']
    return dict(initial=before is None,
        new=[item for number, item in current.items() if number not in previous],
        changed=[item for number, item in current.items()
                 if number in previous and item['digest'] != previous[number]['digest']],
        closed=[item for number, item in previous.items() if number not in current],
        license_notices_changed=bool(before and before['notices'] != after['notices']))


def capture(mirrors, weekday, backup, output):
    """Update one weekday's private snapshots and write a public change summary.

    Args:
        mirrors (list[dict]): Reviewed repository definitions.
        weekday (int): Weekly group number.
        backup (Path): Checkout of the group's private backup branch.
        output (Path): Public summary artifact path.
    """
    repositories = sorted({mirror['upstream'].removeprefix('https://github.com/').removeprefix('https://').removesuffix('.git')
                           for mirror in mirrors if mirror['weekday'] == weekday})
    state_path = backup / 'index.json'
    previous = json.loads(state_path.read_text()) if state_path.exists() else {}
    current, activity = {}, {}
    folder = backup / 'snapshots'
    folder.mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for snapshot in pool.map(collect, repositories):
            repository = snapshot['repository']
            (folder / (repository.replace('/', '--') + '.json')).write_text(
                json.dumps(snapshot, indent=2) + '\n')
            current[repository] = index(snapshot)
            activity[repository] = changes(previous.get(repository), current[repository])
    state_path.write_text(json.dumps(current, indent=2) + '\n')
    output.write_text(json.dumps(dict(weekday=weekday, repositories=current, activity=activity), indent=2) + '\n')


def report(directory, repository, run_url):
    """Update one owned catalog issue and comment when upstream activity changes.

    Args:
        directory (Path): Downloaded public activity artifacts.
        repository (str): Catalog receiving the status issue.
        run_url (str): Workflow containing the snapshots and quality results.
    """
    records, activity, wikis = {}, {}, {}
    for path in sorted(directory.glob('activity-*/activity.json')):
        data = json.loads(path.read_text())
        records.update(data['repositories'])
        activity.update(data['activity'])
    for path in sorted(directory.glob('activity-*/wiki-activity.json')):
        wikis.update(json.loads(path.read_text())['wikis'])
    if not records:
        raise ValueError('No complete upstream activity summaries were produced')
    state_path = ROOT / 'ci/upstream-state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    state.update(records)
    state_path.write_text(json.dumps(state, indent=2) + '\n')
    wiki_path = ROOT / 'ci/wiki-state.json'
    previous_wikis = json.loads(wiki_path.read_text()) if wiki_path.exists() else {}
    wiki_state = dict(previous_wikis, **wikis)
    wiki_path.write_text(json.dumps(wiki_state, indent=2) + '\n')
    lines = [MARKER, 'Weekly upstream activity and source-backup status.', '',
        '| Upstream | Last capture | Open issues | Open PRs | License notices |', '|---|---|---|---|---|']
    updates = []
    for source, record in sorted(state.items()):
        source_url = 'https://' + source if source.startswith('gitlab.com/') else 'https://github.com/' + source
        items = list(record['items'].values())
        delta = activity.get(source, dict(new=[], changed=[], closed=[], initial=False,
                                          license_notices_changed=False))
        lines.append('| [%s](%s) | %s | %s | %s | %s |' % (
            source, source_url, record['captured_at'][:10], sum(item['kind'] == 'issue' for item in items),
            sum(item['kind'] == 'PR' for item in items),
            'Changed; review terms' if delta['license_notices_changed'] else
            'Scan incomplete' if not record['notice_scan_complete'] else 'Recorded'))
        for kind in ('new', 'changed', 'closed'):
            for item in delta[kind]:
                title = item['title'].replace('\n', ' ').replace('\r', ' ').replace('[', '(').replace(']', ')').replace('@', '＠')
                action = 'Initial open' if delta['initial'] else 'No longer open' if kind == 'closed' else kind.capitalize()
                updates.append('- %s %s: [%s](%s)' % (action, item['kind'], title, item['url']))
        if delta['license_notices_changed']:
            updates.append('- License notices changed in [source](%s).' % source_url)
    if wiki_state:
        counts = Counter(record['status'] for record in wiki_state.values())
        lines.extend(['', 'Wiki checks: ' + ', '.join('%s %s' % (count, label)
                      for label, count in sorted(counts.items())) + '.',
                      '[All wiki statuses](https://github.com/weewx-packages/catalog/blob/main/ci/wiki-state.json)',
                      '', '| Wiki | Status | Last verified backup |', '|---|---|---|'])
        for source, record in sorted(wiki_state.items()):
            url = ('https://' + source + '/-/wikis/home' if source.startswith('gitlab.com/')
                   else 'https://github.com/' + source + '/wiki')
            label = record['status'] + ('; last backup retained' if record['retained'] else '')
            if record['status'] in ('saved', 'unavailable') or record['retained']:
                lines.append('| [%s](%s) | %s | %s |' % (
                    source, url, label, (record['last_verified'] or '-')[:10]))
            previous = previous_wikis.get(source, {})
            if source in wikis and (record['status'] != previous.get('status')
                    or record['digest'] != previous.get('digest')):
                if record['status'] == 'saved' or record['retained'] or record['status'] == 'unavailable':
                    updates.append('- Wiki %s: [%s](%s).' % (label, source, url))
    lines.extend(['', '[Workflow and quality results](%s)' % run_url,
                  '[Private discussion and wiki backups](https://github.com/weewx-packages/upstream-backup)', '',
                  'The table shows each repository\'s latest capture. This run updates its assigned groups.',
                  'Full discussion bodies,',
                  'reviews, available PR file patches and restorable wiki Git bundles are kept in the private backup.',
                  'Externally hosted attachments remain linked, not copied.'])
    body = '\n'.join(lines) + '\n'
    issues = api('repos/%s/issues?state=all&per_page=100' % repository, paginate=True)
    if not isinstance(issues, list):
        raise ValueError('Unexpected catalog issue response')
    issue = next((item for item in issues if MARKER in (item.get('body') or '')
                  and item['user']['login'] == 'github-actions[bot]' and 'pull_request' not in item), None)
    if issue is None:
        issue = api('repos/%s/issues' % repository, dict(title='Upstream activity', body=body))
    else:
        api('repos/%s/issues/%s' % (repository, issue['number']), dict(body=body, state='open'), method='PATCH')
    if updates:
        if not isinstance(issue, dict):
            raise ValueError('Unexpected activity issue response')
        message = '\n'.join(updates[:50])
        if len(updates) > 50:
            message += '\n\nFurther changes are recorded in the workflow activity artifacts.'
        api('repos/%s/issues/%s/comments' % (repository, issue['number']),
            dict(body=message + '\n\n[Run details](%s)' % run_url))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['capture', 'report'])
    parser.add_argument('--weekday', type=int, choices=range(1, 6))
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--artifacts', type=Path)
    args = parser.parse_args()
    if args.action == 'capture':
        capture(json.loads((ROOT / 'ci/mirrors.json').read_text()), args.weekday, args.backup, args.output)
    else:
        repository = os.environ['GITHUB_REPOSITORY']
        report(args.artifacts, repository, '%s/%s/actions/runs/%s' %
               (os.environ['GITHUB_SERVER_URL'], repository, os.environ['GITHUB_RUN_ID']))
