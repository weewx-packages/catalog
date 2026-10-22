"""Synchronize reviewed forks in weekly groups without executing upstream code."""

import argparse
import json
import os
from pathlib import Path
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


def sync(mirrors, weekday, keys):
    """Copy one weekly group, continuing other mirrors after a failed sync.

    Args:
        mirrors (list[dict]): Reviewed upstream URLs, forks and assigned weekdays.
        weekday (int): Cron weekday number, Monday through Friday.
        keys (dict): Private deploy keys indexed by destination repository.

    Returns:
        list[str]: Repositories whose sync failed or whose deploy key is missing.
    """
    failed = []
    # Keys belong to the trusted mirror job. Git subprocesses receive only the
    # path to their own key, never the bundle of keys for the whole weekday.
    env = {key: value for key, value in os.environ.items() if key != 'MIRROR_SSH_KEYS'}
    with tempfile.TemporaryDirectory() as directory:
        key_path = Path(directory) / 'key'
        known_hosts = Path(directory) / 'known_hosts'
        meta = json.loads(subprocess.check_output(['gh', 'api', 'meta'], text=True, env=env))
        known_hosts.write_text(''.join('github.com ' + key + '\n' for key in meta['ssh_keys']))
        for mirror in mirrors:
            if mirror['weekday'] != weekday or not mirror.get('sync', True):
                continue
            fork = mirror['fork']
            if not fork.startswith('weewx-packages/') or fork.count('/') != 1:
                raise ValueError('Mirror target must belong to weewx-packages')
            if fork not in keys:
                print('Missing deploy key for ' + fork, flush=True)
                failed.append(fork)
                continue
            key_path.write_text(keys[fork])
            key_path.chmod(0o600)
            env['GIT_SSH_COMMAND'] = shlex.join(['ssh', '-i', str(key_path),
                '-o', 'IdentitiesOnly=yes', '-o', 'StrictHostKeyChecking=yes',
                '-o', 'UserKnownHostsFile=' + str(known_hosts)])
            print('Synchronizing ' + fork, flush=True)
            result = subprocess.run(['bash', str(ROOT / 'ci/sync-weewx.sh'),
                mirror['upstream'], 'git@github.com:' + fork + '.git'], env=env)
            if result.returncode:
                failed.append(fork)
    return failed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['matrix', 'checks', 'sync'])
    parser.add_argument('--schedule', default='')
    parser.add_argument('--weekday', type=int, choices=range(1, 6))
    args = parser.parse_args()
    mirrors = json.loads((ROOT / 'ci/mirrors.json').read_text())
    if args.action in ('matrix', 'checks'):
        select = matrix if args.action == 'matrix' else check_matrix
        print(json.dumps(select(mirrors, args.schedule)))
    else:
        if args.weekday is None:
            parser.error('sync requires --weekday')
        failures = sync(mirrors, args.weekday, json.loads(os.environ.pop('MIRROR_SSH_KEYS')))
        if failures:
            raise SystemExit('Failed mirrors: ' + ', '.join(failures))
