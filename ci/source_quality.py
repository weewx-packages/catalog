"""Check mirrored source installation with WeeWX, separately from backup credentials."""

import argparse
import json
import os
from pathlib import Path
import py_compile
import subprocess
import sys

from compatibility import command, github
from issues import reconcile, result_name

ROOT = Path(__file__).resolve().parents[1]


def check(mirror, branch, weewx_sha, work):
    """Compile runtime Python and install a source archive into an isolated station.

    Args:
        mirror (dict): Reviewed fork and its check profile.
        branch (str): WeeWX branch under test.
        weewx_sha (str): Installed WeeWX source commit.
        work (Path): Empty working directory for this repository.

    Returns:
        tuple[dict, dict]: Resolved issue-report case and installation result.
    """
    work.mkdir(parents=True)
    source = work / 'source'
    case = dict(package=mirror['fork'].split('/')[1], repository=mirror['fork'],
                branch=branch, python='3.14', weewx_sha=weewx_sha,
                weewx_repository='weewx/weewx', source_sha='not-checked', coverage='installation',
                release={'version': 'source', 'archive': {'url': 'https://github.com/' + mirror['fork']}})
    status, phase, details = 'error', 'checkout', []
    try:
        command(['git', 'clone', '--depth=1', 'https://github.com/' + mirror['fork'] + '.git', str(source)])
        sha = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
        case.update(source_sha=sha, release=dict(version='source ' + sha[:12], archive={
                    'url': 'https://github.com/%s/archive/%s.zip' % (mirror['fork'], sha)}))
        if not (source / 'install.py').is_file():
            return case, dict(status='not-covered', phase='profile', details=[
                'No root install.py; requires a project-specific WeeWX test profile.'])
        status, phase = 'failed', 'syntax'
        files = [source / 'install.py']
        if (source / 'bin').is_dir():
            files.extend((source / 'bin').rglob('*.py'))
        for path in files:
            py_compile.compile(str(path), doraise=True)
        phase = 'installation'
        station = work / 'station'
        config = station / 'weewx.conf'
        archive = work / 'package.zip'
        command(['git', '-C', str(source), 'archive', '--format=zip', '--prefix=extension/',
                 '--output=' + str(archive), sha])
        command(['weectl', 'station', 'create', str(station), '--no-prompt'])
        command([sys.executable, '-c', 'import sys,weecfg,weewx.manager; '
            '_,c=weecfg.read_config(sys.argv[1]); '
            'weewx.manager.open_manager_with_config(c,"wx_binding",initialize=True).close()', str(config)])
        command(['weectl', 'extension', 'install', str(archive), '--config', str(config), '--yes'],
                input_text=mirror.get('install_input', ''))
        status = 'passed'
    except (OSError, subprocess.SubprocessError, py_compile.PyCompileError) as error:
        details.append(str(error))
    return case, dict(status=status, phase=phase, details=details)


def run(mirrors, weekday, branch, weewx_sha, output):
    """Run every installation profile in one weekly group, retaining failed results.

    Args:
        mirrors (list[dict]): Reviewed source backup definitions.
        weekday (int): Assigned cron weekday.
        branch (str): WeeWX branch under test.
        weewx_sha (str): Actual WeeWX checkout commit.
        output (Path): New artifact directory.

    Returns:
        int: Nonzero when at least one check failed or could not run.
    """
    output.mkdir(parents=True)
    cases, failed = [], False
    for mirror in mirrors:
        if mirror['weekday'] != weekday or mirror['check'] != 'installation':
            continue
        case, result = check(mirror, branch, weewx_sha, output / mirror['fork'].split('/')[1])
        cases.append(case)
        folder = output / result_name(case)
        folder.mkdir()
        (folder / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        failed |= result['status'] in ('failed', 'error')
    (output / 'matrix.json').write_text(json.dumps(dict(weekday=weekday, include=cases), indent=2) + '\n')
    return int(failed)


def report(directory):
    """Maintain installation issues only after accounting for both WeeWX branches.

    Args:
        directory (Path): Downloaded quality artifacts.
    """
    groups, cases, results = set(), [], {}
    for plan_path in sorted(directory.glob('quality-*/matrix.json')):
        plan = json.loads(plan_path.read_text())
        groups.add(plan['weekday'])
        for case in plan['include']:
            cases.append(case)
            path = plan_path.parent / result_name(case) / 'result.json'
            if path.is_file():
                results[result_name(case)] = json.loads(path.read_text())
    mirrors = json.loads((ROOT / 'ci/mirrors.json').read_text())
    for mirror in mirrors:
        if mirror['weekday'] not in groups or mirror['check'] != 'installation':
            continue
        package = mirror['fork'].split('/')[1]
        available = [case for case in cases if case['package'] == package]
        if not available:
            continue
        for branch in ('master', 'development'):
            if not any(case['branch'] == branch for case in available):
                cases.append(dict(available[0], branch=branch, weewx_sha='not-checked'))
    issues = []
    page = 1
    while True:
        batch = github('repos/%s/issues?state=all&per_page=100&page=%s' %
                       (os.environ['GITHUB_REPOSITORY'], page))
        issues.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    repository = os.environ['GITHUB_REPOSITORY']
    url = '%s/%s/actions/runs/%s' % (os.environ['GITHUB_SERVER_URL'], repository, os.environ['GITHUB_RUN_ID'])
    state_path = ROOT / 'ci/source-quality.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    for case in cases:
        name = result_name(case)
        state[name] = dict(case=case, result=results.get(name, {'status': 'missing'}), run=url)
    state_path.write_text(json.dumps(state, indent=2) + '\n')
    reconcile(cases, results, issues, repository, url)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['run', 'report'])
    parser.add_argument('--weekday', type=int, choices=range(1, 6))
    parser.add_argument('--branch', choices=['master', 'development'])
    parser.add_argument('--weewx-sha')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--artifacts', type=Path)
    args = parser.parse_args()
    if args.action == 'run':
        sys.exit(run(json.loads((ROOT / 'ci/mirrors.json').read_text()), args.weekday,
                     args.branch, args.weewx_sha, args.output))
    report(args.artifacts)
