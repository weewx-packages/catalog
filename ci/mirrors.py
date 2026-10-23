"""Synchronize reviewed forks one at a time without executing upstream code."""

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def matrix(mirrors, schedule):
    """Select weekly groups, or every configured group for a manual run.

    Args:
        mirrors (list[dict]): Reviewed upstream URLs, forks and assigned weekdays.
        schedule (str): Triggering cron expression, or an empty string for manual runs.

    Returns:
        dict: GitHub Actions matrix containing the selected weekday groups.
    """
    weekdays = sorted({mirror['weekday'] for mirror in mirrors})
    if any(day not in range(1, 6) for day in weekdays):
        raise ValueError('Mirror weekdays must be Monday through Friday')
    if schedule:
        weekdays = [day for day in weekdays if day == int(schedule.split()[-1])]
    return {'include': [{'weekday': day} for day in weekdays]}


def check_matrix(mirrors, schedule):
    """Select raw-source checks that have not moved to project-specific CI.

    Args:
        mirrors (list[dict]): Reviewed source definitions and check routes.
        schedule (str): Triggering cron, or an empty string for all weekly groups.

    Returns:
        dict: Weekday and WeeWX branch for each required source-check job.
    """
    selected = {group['weekday'] for group in matrix(mirrors, schedule)['include']}
    weekdays = sorted({item['weekday'] for item in mirrors
                       if item['weekday'] in selected and item['check'] == 'installation'})
    return {'include': [dict(weekday=day, branch=branch)
                        for day in weekdays for branch in ('master', 'development')]}


def secret_name(fork):
    """Return the name of the environment secret that holds a mirror's deploy key.

    Args:
        fork (str): Destination repository (e.g., 'weewx-packages/weewx-gw1000').

    Returns:
        str: Secret name (e.g., 'MIRROR_KEY_WEEWX_GW1000').
    """
    return 'MIRROR_KEY_' + re.sub(r'[^A-Z0-9]', '_', fork.split('/', 1)[-1].upper())


def repositories(mirrors, schedule):
    """Select one sync job per synchronized mirror of the scheduled weekdays.

    Args:
        mirrors (list[dict]): Reviewed upstream URLs, forks and assigned weekdays.
        schedule (str): Triggering cron expression, or an empty string for manual runs.

    Returns:
        dict: GitHub Actions matrix with weekday, fork and secret for each job.

    Raises:
        ValueError: Two forks map to the same secret name.
    """
    owners = {}
    for mirror in mirrors:
        if mirror.get('sync', True):
            # Secret names only allow letters, digits and underscores, so
            # 'a-b' and 'a_b' would share a key. Refuse that instead of letting
            # one mirror push with the other's key.
            owner = owners.setdefault(secret_name(mirror['fork']), mirror['fork'])
            if owner != mirror['fork']:
                raise ValueError('Forks share a secret name: %s, %s' % (owner, mirror['fork']))
    selected = {group['weekday'] for group in matrix(mirrors, schedule)['include']}
    return {'include': [dict(weekday=mirror['weekday'], fork=mirror['fork'],
                             secret=secret_name(mirror['fork']))
                        for mirror in mirrors
                        if mirror.get('sync', True) and mirror['weekday'] in selected]}


def sync(mirrors, fork, key):
    """Copy one upstream into its fork with that fork's own deploy key.

    Args:
        mirrors (list[dict]): Reviewed upstream URLs, forks and assigned weekdays.
        fork (str): Destination repository selected by the workflow matrix.
        key (str): Private deploy key of this fork. Empty if the secret is missing.

    Returns:
        bool: True if the refs were copied or the fork is not synchronized.

    Raises:
        ValueError: The fork is unknown or outside weewx-packages.
    """
    if not fork.startswith('weewx-packages/') or fork.count('/') != 1:
        raise ValueError('Mirror target must belong to weewx-packages')
    mirror = next((item for item in mirrors if item['fork'] == fork), None)
    if mirror is None:
        raise ValueError('Fork is not listed in ci/mirrors.json: ' + fork)
    if not mirror.get('sync', True):
        return True
    if not key.strip():
        print('Missing deploy key for %s in secret %s' % (fork, secret_name(fork)), flush=True)
        return False
    # The key belongs to the trusted mirror job. The git subprocess receives
    # only the path to the key file, never the key in its environment.
    env = {name: value for name, value in os.environ.items() if name != 'MIRROR_SSH_KEY'}
    with tempfile.TemporaryDirectory() as directory:
        key_path = Path(directory) / 'key'
        known_hosts = Path(directory) / 'known_hosts'
        meta = json.loads(subprocess.check_output(['gh', 'api', 'meta'], text=True, env=env))
        known_hosts.write_text(''.join('github.com ' + line + '\n' for line in meta['ssh_keys']))
        key_path.write_text(key.strip() + '\n')
        key_path.chmod(0o600)
        env['GIT_SSH_COMMAND'] = shlex.join(['ssh', '-i', str(key_path),
            '-o', 'IdentitiesOnly=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'UserKnownHostsFile=' + str(known_hosts)])
        print('Synchronizing ' + fork, flush=True)
        result = subprocess.run(['bash', str(ROOT / 'ci/sync-weewx.sh'),
            mirror['upstream'], 'git@github.com:' + fork + '.git'], env=env)
    return result.returncode == 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['matrix', 'repositories', 'checks', 'sync'])
    parser.add_argument('--schedule', default='')
    parser.add_argument('--fork')
    args = parser.parse_args()
    mirrors = json.loads((ROOT / 'ci/mirrors.json').read_text())
    if args.action != 'sync':
        select = dict(matrix=matrix, repositories=repositories, checks=check_matrix)[args.action]
        print(json.dumps(select(mirrors, args.schedule)))
    else:
        if args.fork is None:
            parser.error('sync requires --fork')
        if not sync(mirrors, args.fork, os.environ.pop('MIRROR_SSH_KEY', '')):
            raise SystemExit('Failed mirror: ' + args.fork)
