"""Give mirrors their own deploy key and catalog environment secret.

Run locally with a gh login that administers the organization. Private keys
exist only in a temporary directory and are never printed:

    python3 ci/mirror_keys.py add weewx-packages/weewx-gw1000
    python3 ci/mirror_keys.py add --all

Each run replaces only the keys of the named forks. The other mirrors keep
theirs, so adding a mirror never rotates a whole weekday.
"""

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import mirrors

CATALOG = 'weewx-packages/catalog'
TITLE = 'catalog mirror'


def api(path, data=None, method=None):
    """Call the GitHub REST API through gh.

    Args:
        path (str): API path below https://api.github.com/.
        data (dict|None): JSON request body, or None for no body.
        method (str|None): HTTP method. Default is GET, or POST with a body.

    Returns:
        dict|list|None: Decoded JSON response, or None for an empty response.
    """
    args = ['gh', 'api', path]
    if method:
        args += ['--method', method]
    if data is not None:
        args += ['--input', '-']
    result = subprocess.run(args, input=json.dumps(data) if data is not None else None,
                            text=True, capture_output=True, check=True)
    return json.loads(result.stdout) if result.stdout.strip() else None


def environment(weekday):
    """Create the weekday environment and restrict it to the main branch.

    Args:
        weekday (int): Cron weekday number, Monday through Friday.

    Returns:
        str: Environment name (e.g., 'mirrors-1').
    """
    name = 'mirrors-%d' % weekday
    api('repos/%s/environments/%s' % (CATALOG, name), method='PUT', data=dict(
        deployment_branch_policy=dict(protected_branches=False, custom_branch_policies=True)))
    policies = api('repos/%s/environments/%s/deployment-branch-policies' % (CATALOG, name))
    if not any(policy['name'] == 'main' for policy in policies['branch_policies']):
        api('repos/%s/environments/%s/deployment-branch-policies' % (CATALOG, name),
            method='POST', data=dict(name='main', type='branch'))
    return name


def add(mirror, directory):
    """Install a new deploy key on a fork and store its private half as a secret.

    The new key is in place before the old ones are deleted, so a sync running
    at the same time keeps working with the key it already has.

    Args:
        mirror (dict): Entry from ci/mirrors.json with fork and weekday.
        directory (Path): Private temporary directory for the key pair.
    """
    fork = mirror['fork']
    old = [key['id'] for key in api('repos/%s/keys' % fork) if key['title'] == TITLE]
    path = directory / mirror['fork'].replace('/', '_')
    subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-C', TITLE, '-f', str(path)],
                   check=True)
    api('repos/%s/keys' % fork, method='POST', data=dict(
        title=TITLE, key=Path(str(path) + '.pub').read_text().strip(), read_only=False))
    subprocess.run(['gh', 'secret', 'set', mirrors.secret_name(fork), '--repo', CATALOG,
                    '--env', environment(mirror['weekday'])],
                   input=path.read_text(), text=True, capture_output=True, check=True)
    for key_id in old:
        api('repos/%s/keys/%s' % (fork, key_id), method='DELETE')
    print('Stored %s in mirrors-%d' % (mirrors.secret_name(fork), mirror['weekday']), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', choices=['add'])
    parser.add_argument('forks', nargs='*')
    parser.add_argument('--all', action='store_true', help='every synchronized mirror')
    args = parser.parse_args()
    entries = json.loads((mirrors.ROOT / 'ci/mirrors.json').read_text())
    # Validates that no two forks share a secret name before any key changes.
    selected = mirrors.repositories(entries, '')['include']
    if not args.all:
        unknown = set(args.forks) - {item['fork'] for item in selected}
        if unknown or not args.forks:
            parser.error('name synchronized forks from ci/mirrors.json, or use --all: '
                         + ', '.join(sorted(unknown)))
        selected = [item for item in selected if item['fork'] in args.forks]
    with tempfile.TemporaryDirectory(prefix='mirror-keys-') as directory:
        for item in selected:
            add(item, Path(directory))
