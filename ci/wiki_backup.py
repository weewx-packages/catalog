"""Keep restorable wiki histories in the private weekly backup, without checkout."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlencode

from compatibility import github
from gitlab_status import get

ROOT = Path(__file__).resolve().parents[1]


def wiki_url(repository):
    """Build a public wiki URL, rejecting names that could escape the backup tree.

    Args:
        repository (str): GitHub owner/repository or gitlab.com/namespace/project.

    Returns:
        str: HTTPS Git URL for the separate wiki repository.
    """
    parts = repository.split('/')
    if len(parts) < 2 or any(part in ('', '.', '..') or '\\' in part for part in parts):
        raise ValueError('Invalid wiki repository: ' + repository)
    host = '' if repository.startswith('gitlab.com/') else 'github.com/'
    return 'https://' + host + repository + '.wiki.git'


def targets(mirrors, weekday):
    """Select upstream and organization wikis using stable weekly assignments.

    Args:
        mirrors (list[dict]): Reviewed upstreams, organization forks and weekdays.
        weekday (int): Assigned weekly group, Monday through Friday.

    Returns:
        dict: Repository names mapped to wiki URLs and optional enabled flags.
    """
    selected = {}
    for mirror in mirrors:
        if mirror['weekday'] == weekday:
            source = mirror['upstream'].removeprefix('https://github.com/').removeprefix('https://').removesuffix('.git')
            selected[source] = dict(url=wiki_url(source), enabled=None)
    assignments = {item['fork']: item['weekday'] for item in mirrors}
    page = 1
    while True:
        repositories = github('orgs/weewx-packages/repos?type=public&per_page=100&page=%s' % page)
        for repository in repositories:
            name = repository['full_name']
            day = assignments.get(name, int(hashlib.sha256(name.encode()).hexdigest()[:8], 16) % 5 + 1)
            if day != weekday:
                continue
            selected[name] = dict(url=wiki_url(name), enabled=repository['has_wiki'])
            # Additional forks, including the core mirror, are not extension
            # entries. Include their upstream wiki as well as their own wiki.
            if name not in assignments and repository['fork']:
                parent = github('repos/' + name)['parent']
                source = parent['full_name']
                selected[source] = dict(url=wiki_url(source), enabled=parent['has_wiki'])
        if len(repositories) < 100:
            return selected
        page += 1


def git(arguments):
    """Run Git without interactive credentials or checking out upstream files.

    Args:
        arguments (list[str]): Git arguments, including any repository directory.

    Returns:
        str: Captured standard output; failures retain their diagnostic stderr.
    """
    # An absent public wiki otherwise prompts for credentials just like a
    # private repository. Use gh's existing token without persisting it in Git.
    credentials = ['-c', 'credential.https://github.com.helper=',
                   '-c', 'credential.https://github.com.helper=!gh auth git-credential']
    return subprocess.run(['git', *credentials, *arguments], text=True, capture_output=True,
                          env=dict(os.environ, GIT_TERMINAL_PROMPT='0'),
                          check=True, timeout=120).stdout


def refs(directory):
    """Read all named refs from a bare repository."""
    return dict(line.split(' ', 1) for line in git([
        '-C', str(directory), 'for-each-ref', '--format=%(refname) %(objectname)']).splitlines())


def capture_wiki(repository, target, backup, previous):
    """Replace a wiki bundle only after an independent restore has passed.

    Args:
        repository (str): Validated source name, also used for its relative path.
        target (dict): Wiki URL and enabled flag; None means not yet known.
        backup (Path): Private backup checkout.
        previous (dict): Last observation, including the last verified bundle.

    Returns:
        dict: Current status and, when available, the last restorable backup.
    """
    wiki_url(repository)
    record = dict(url=target['url'], checked_at=datetime.now(timezone.utc).isoformat(),
                  status='unavailable')
    if previous.get('backup'):
        record['backup'] = previous['backup']
    try:
        enabled = target['enabled']
        if enabled is None and repository.startswith('gitlab.com/'):
            query = '{project(fullPath:%s){wikiEnabled}}' % json.dumps(repository.removeprefix('gitlab.com/'))
            response = get('https://gitlab.com/api/graphql?' + urlencode({'query': query}))
            enabled = response['data']['project']['wikiEnabled']
        if enabled is False:
            return dict(record, status='disabled')
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            source = work / 'source.git'
            git(['clone', '--mirror', '--quiet', target['url'], str(source)])
            current_refs = refs(source)
            if not current_refs:
                return dict(record, status='empty')
            head = git(['-C', str(source), 'rev-parse', 'HEAD']).strip()
            destination = backup / 'wikis' / (repository + '.bundle')
            saved = previous.get('backup', {})
            if (saved.get('refs') == current_refs and saved.get('head') == head
                    and destination.is_file()
                    and hashlib.sha256(destination.read_bytes()).hexdigest() == saved.get('sha256')):
                bundle = destination
            else:
                bundle = work / 'wiki.bundle'
                git(['-C', str(source), 'bundle', 'create', str(bundle), '--all'])
            restored = work / 'restored.git'
            git(['clone', '--mirror', '--quiet', str(bundle), str(restored)])
            git(['-C', str(restored), 'fsck', '--full'])
            if refs(restored) != current_refs or git(['-C', str(restored), 'rev-parse', 'HEAD']).strip() != head:
                raise ValueError('Restored wiki refs differ from the source')
            if bundle != destination:
                destination.parent.mkdir(parents=True, exist_ok=True)
                staged = destination.with_suffix('.bundle.tmp')
                staged.write_bytes(bundle.read_bytes())
                staged.replace(destination)
            record.update(status='saved', backup=dict(path=str(destination.relative_to(backup)),
                sha256=hashlib.sha256(destination.read_bytes()).hexdigest(), refs=current_refs,
                head=head, verified_at=record['checked_at']))
    except subprocess.CalledProcessError as error:
        record['error'] = error.stderr.strip()
        if 'Repository not found' in error.stderr and target['url'].startswith('https://github.com/'):
            record['status'] = 'absent'
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        record['error'] = str(error)
    return record


def capture(mirrors, weekday, backup, output):
    """Capture every selected wiki and keep good bundles after remote failures.

    Args:
        mirrors (list[dict]): Source definitions with weekly assignments.
        weekday (int): Selected weekly group.
        backup (Path): Checkout of that group's private backup branch.
        output (Path): Public status summary; never contains wiki bodies.

    Returns:
        int: Nonzero for unavailable wikis or disappearance of an existing backup.
    """
    state_path = backup / 'wiki-index.json'
    previous = json.loads(state_path.read_text()) if state_path.exists() else {}
    selected = targets(mirrors, weekday)
    # A removed organization repository must still be probed. Removing it from
    # discovery must not discard its last backup or silently stop monitoring it.
    for repository, record in previous.items():
        selected.setdefault(repository, dict(url=record['url'], enabled=None))
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(lambda repository: (repository, capture_wiki(
            repository, selected[repository], backup, previous.get(repository, {}))), sorted(selected)))
    current = dict(records)
    state_path.write_text(json.dumps(current, indent=2) + '\n')
    public = {repository: {key: record[key] for key in ('url', 'checked_at', 'status')}
              for repository, record in records}
    for repository, record in records:
        public[repository]['last_verified'] = record.get('backup', {}).get('verified_at')
        public[repository]['digest'] = record.get('backup', {}).get('sha256')
        public[repository]['retained'] = bool(record.get('backup') and record['status'] != 'saved')
    output.write_text(json.dumps(dict(weekday=weekday, wikis=public), indent=2) + '\n')
    return int(any(record['status'] == 'unavailable' or record['retained'] for record in public.values()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--weekday', type=int, choices=range(1, 6), required=True)
    parser.add_argument('--backup', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(capture(json.loads((ROOT / 'ci/mirrors.json').read_text()),
                             args.weekday, args.backup, args.output))
