"""Maintain one compatibility issue per package from completed matrix results.

Run separately from extension code, with issue-write permission only in this
job. Missing results and infrastructure errors prevent recovery closure.
"""

import json
import os
from pathlib import Path
import sys

from compatibility import github


def result_name(case):
    """Return the artifact name shared by the test and reporting jobs.

    Args:
        case (dict): A resolved matrix case.

    Returns:
        str: Package, branch and Python identifying this result.
    """
    return 'result-%s-%s-%s' % (case['package'], case['branch'], case['python'])


def issue_body(package, cases, results, run_url):
    """Describe failed checks with exact revisions and their workflow log.

    Args:
        package (str): Catalog package ID.
        cases (list[dict]): All expected cases for this package.
        results (dict): Results indexed by artifact name.
        run_url (str): Workflow run with the full logs and JUnit artifacts.

    Returns:
        str: Issue body, including the automation's stable ownership marker.
    """
    first = cases[0]
    rows = ['<!-- weewx-compatibility:%s -->' % package,
            'The published %s %s fails compatibility checks.' %
            (package, first['release']['version']), '',
            '| WeeWX branch | Commit | Python | Result |', '|---|---|---|---|']
    for case in cases:
        result = results[result_name(case)]
        commit = case['weewx_sha']
        rows.append('| %s | [%s](https://github.com/weewx/weewx/commit/%s) | %s | %s |' %
                    (case['branch'], commit[:12], commit, case['python'], result['status']))
    for case in cases:
        result = results[result_name(case)]
        if result['status'] == 'failed':
            rows.extend(['', 'Failure in %s on %s / Python %s:' %
                         (result['phase'], case['branch'], case['python']),
                         '````text', '\n'.join(result['details'])[:2500].replace('`', "'"), '````', ''])
    rows.extend(['', '[Test logs and artifacts](%s)' % run_url,
                 '[Release archive](%s) · [Test source](https://github.com/%s/tree/%s)' %
                 (first['release']['archive']['url'], first['repository'], first['source_sha'])])
    return '\n'.join(rows) + '\n'


def reconcile(cases, results, issues, repo, run_url):
    """Create, update, reopen or close only this automation's package issues.

    Args:
        cases (list[dict]): Expected cases from the preparation job.
        results (dict): Available results indexed by artifact name.
        issues (list[dict]): Existing issues, including closed issues.
        repo (str): GitHub owner/repository receiving issues.
        run_url (str): Workflow run supplying the results.
    """
    for package in sorted({case['package'] for case in cases}):
        checks = [case for case in cases if case['package'] == package]
        states = [results.get(result_name(case), {}).get('status') for case in checks]
        marker = '<!-- weewx-compatibility:%s -->' % package
        existing = next((issue for issue in issues
                         if issue['user']['login'] == 'github-actions[bot]'
                         and marker in (issue.get('body') or '') and 'pull_request' not in issue), None)
        if 'failed' in states:
            # Missing jobs remain visible in the table, but cannot hide the
            # confirmed failure from another Python or WeeWX branch.
            available = {result_name(case): results.get(result_name(case), {'status': 'missing'})
                         for case in checks}
            body = issue_body(package, checks, available, run_url)
            title = '%s %s: WeeWX compatibility failure' % (package, checks[0]['release']['version'])
            if existing is None:
                github('repos/%s/issues' % repo,
                       {'title': title, 'body': body, 'labels': ['compatibility']})
            elif existing['body'] != body or existing['state'] != 'open':
                github('repos/%s/issues/%s' % (repo, existing['number']),
                       {'title': title, 'body': body, 'state': 'open'}, method='PATCH')
        elif all(state == 'passed' for state in states) and existing and existing['state'] == 'open':
            github('repos/%s/issues/%s/comments' % (repo, existing['number']),
                   {'body': 'All checks passed: [test logs](%s).' % run_url})
            github('repos/%s/issues/%s' % (repo, existing['number']),
                   {'state': 'closed', 'state_reason': 'completed'}, method='PATCH')


if __name__ == '__main__':
    directory = Path(sys.argv[1])
    cases = json.loads((directory / 'plan/matrix.json').read_text())['include']
    results = {}
    summary = ['## WeeWX compatibility', '', '| Package | WeeWX | Python | Result |', '|---|---|---|---|']
    for case in cases:
        path = directory / result_name(case) / 'result.json'
        result = json.loads(path.read_text()) if path.is_file() else {'status': 'missing'}
        results[result_name(case)] = result
        summary.append('| %s | %s | %s | %s |' %
                       (case['package'], case['branch'], case['python'], result['status']))
    if 'GITHUB_STEP_SUMMARY' in os.environ:
        Path(os.environ['GITHUB_STEP_SUMMARY']).write_text('\n'.join(summary) + '\n')
    if os.environ.get('PUBLISH_ISSUES') == 'true':
        repo = os.environ['GITHUB_REPOSITORY']
        issues = []
        page = 1
        while True:
            batch = github('repos/%s/issues?state=all&per_page=100&page=%s' % (repo, page))
            issues.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        url = '%s/%s/actions/runs/%s' % (os.environ['GITHUB_SERVER_URL'], repo, os.environ['GITHUB_RUN_ID'])
        reconcile(cases, results, issues, repo, url)
    sys.exit(int(any(result['status'] != 'passed' for result in results.values())))
