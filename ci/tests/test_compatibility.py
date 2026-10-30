"""Exercise missing coverage, unsafe archives and misleading green results."""

import json
from pathlib import Path
import subprocess
import sys
import tarfile
from unittest.mock import Mock
import zipfile

import pytest

CI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CI))
import compatibility as compat
import issues


@pytest.fixture
def package():
    """Supply a catalog entry whose release array is deliberately unordered."""
    return {'id': 'example', 'installer_name': 'example', 'releases': [
        {'version': '2.0.0rc1'}, {'version': '1.2.0'},
        {'version': '1.10.0'}, {'version': '1.11.0', 'yanked': True},
    ]}


def test_latest_ignores_yanked_and_prerelease_versions(package):
    assert compat.latest_release(package)['version'] == '1.10.0'


@pytest.mark.parametrize('checks', [{}, {'another': {}}])
def test_new_packages_cannot_silently_escape_testing(package, checks):
    with pytest.raises(ValueError, match='exactly one'):
        compat.matrix({'packages': [package]}, checks)


def test_duplicate_package_ids_are_rejected(package):
    with pytest.raises(ValueError, match='exactly one'):
        compat.matrix({'packages': [package, package]}, {'example': {}})


@pytest.mark.parametrize('requirement', ['weewx>=5', 'WeeWX==5.0', '--upgrade'])
def test_dependencies_cannot_override_core_or_supply_pip_options(package, monkeypatch, requirement):
    monkeypatch.setattr(compat, 'revision', Mock(return_value='sha'))
    with pytest.raises(ValueError):
        compat.matrix({'packages': [package]}, {'example': dict(
            repository='owner/example', ref='v{version}', pip_packages=[requirement])})


def test_each_branch_is_pinned_once_for_the_entire_matrix(package, monkeypatch):
    api = Mock(side_effect=[{'sha': 'master-sha'}, {'sha': 'dev-sha'}, {'sha': 'release-sha'}])
    monkeypatch.setattr(compat, 'github', api)
    plan = compat.matrix({'packages': [package]}, {'example': {
        'repository': 'owner/example', 'ref': 'v{version}', 'imports': ['user.example'],
        'allowed_skips': []}})
    assert len(plan['include']) == 4
    assert {case['weewx_sha'] for case in plan['include']} == {'master-sha', 'dev-sha'}
    assert {case['source_sha'] for case in plan['include']} == {'release-sha'}
    assert {case['weewx_repository'] for case in plan['include']} == {'weewx-packages/weewx'}
    assert api.call_args_list[0].args == ('repos/weewx-packages/weewx/commits/master',)
    assert api.call_args_list[1].args == ('repos/weewx-packages/weewx/commits/development',)
    assert api.call_args_list[-1].args == ('repos/owner/example/commits/v1.10.0',)


@pytest.mark.parametrize('name', ['../escaped.py', '/tmp/escaped.py'])
def test_archive_paths_cannot_escape(tmp_path, name):
    archive = tmp_path / 'bad.zip'
    with zipfile.ZipFile(archive, 'w') as bundle:
        bundle.writestr(name, 'bad')
    with pytest.raises(ValueError, match='escapes'):
        compat.unpack(archive, tmp_path / 'payload')
    assert not (tmp_path / 'escaped.py').exists()


def test_tar_links_are_rejected(tmp_path):
    archive = tmp_path / 'bad.tar'
    with tarfile.open(archive, 'w') as bundle:
        link = tarfile.TarInfo('package/link')
        link.type = tarfile.SYMTYPE
        link.linkname = '/tmp'
        bundle.addfile(link)
    with pytest.raises(ValueError, match='link'):
        compat.unpack(archive, tmp_path / 'payload')


@pytest.mark.parametrize('cases,allowed,expected', [
    ('<testcase name="one"><skipped message="missing WeeWX"/></testcase>', [], 'No tests executed'),
    ('<testcase name="one"/><testcase name="two"><skipped message="missing PHP"/></testcase>',
     [], 'unexpected skip'),
    ('<testcase name="one"><skipped message="optional feature"/></testcase>',
     ['optional feature'], 'No tests executed'),
    ('<testcase name="one"/><testcase name="two"><skipped message="optional feature"/></testcase>',
     ['optional feature'], None),
])
def test_skips_do_not_hide_missing_coverage(tmp_path, cases, allowed, expected):
    report = tmp_path / 'junit.xml'
    report.write_text('<testsuites><testsuite>' + cases + '</testsuite></testsuites>')
    failures = compat.test_failures(report, allowed)
    assert any(expected in failure for failure in failures) if expected else failures == []


def test_download_failure_is_not_a_compatibility_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(compat.urllib.request, 'urlopen', Mock(side_effect=OSError('offline')))
    case = {'release': {'archive': {'url': 'https://example.test/package.zip', 'format': 'zip'}}}
    assert compat.run(case, tmp_path, tmp_path / 'work') == 1
    result = json.loads((tmp_path / 'work/result.json').read_text())
    assert result['status'] == 'error'
    assert result['details'] == ['offline']


def test_transitive_dependencies_keep_the_installed_core_version(tmp_path, monkeypatch):
    monkeypatch.setattr(compat.importlib.metadata, 'version', Mock(return_value='5.6.0'))
    monkeypatch.setattr(compat.urllib.request, 'urlopen', Mock(side_effect=OSError('offline')))
    install = Mock()
    monkeypatch.setattr(compat, 'command', install)
    case = dict(pip_packages=['influxdb-client>=1'], release=dict(archive=dict(
        url='https://example.test/package.zip', format='zip')))
    assert compat.run(case, tmp_path, tmp_path / 'work') == 1
    args = install.call_args.args[0]
    assert '--constraint' in args
    assert Path(args[args.index('--constraint') + 1]).read_text() == 'weewx==5.6.0\n'


@pytest.mark.parametrize('execute_tests', [True, False])
def test_suite_uses_archive_code_even_when_source_checkout_is_fixed(tmp_path, monkeypatch, execute_tests):
    """A passing source checkout must not mask a broken published release."""
    import hashlib

    monkeypatch.setitem(sys.modules, 'weewx', Mock(__version__='5.5.2'))
    source = tmp_path / 'source'
    (source / 'tests').mkdir(parents=True)
    (source / 'tests/test_payload.py').write_text('def test_payload():\n    import broken_payload\n')
    (source / 'broken_payload.py').write_text('# Fixed, but never shipped\n')
    archive = tmp_path / 'release.zip'
    with zipfile.ZipFile(archive, 'w') as bundle:
        bundle.writestr('package/install.py', '')
        bundle.writestr('package/broken_payload.py', 'raise RuntimeError("broken release payload")\n')
    case = {'release': {'requires_python': '>=3.10', 'requires_weewx': '>=5',
                        'archive': {'url': archive.as_uri(), 'format': 'zip',
                                    'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}},
            'imports': [], 'allowed_skips': []}
    real_command = compat.command

    def only_run_pytest(args, cwd=None, env=None):
        if execute_tests and '-m' in args and 'pytest' in args:
            return real_command(args, cwd=cwd, env=env)

    monkeypatch.setattr(compat, 'command', only_run_pytest)
    work = tmp_path / 'work'
    assert compat.run(case, source, work) == 1
    result = json.loads((work / 'result.json').read_text())
    assert result['status'] == 'failed'
    expected = 'broken release payload' if execute_tests else 'No JUnit report'
    assert any(expected in detail for detail in result['details'])


@pytest.mark.parametrize('profile', [{}, {'kind': 'skin'}, {'tests_path': 'ci/project_tests/example'}])
def test_every_installation_checks_repository_paths(tmp_path, monkeypatch, profile):
    """Source suites and skin suites must enforce the same installer contract."""
    import hashlib

    monkeypatch.setitem(sys.modules, 'weewx', Mock(__version__='5.5.2'))
    source = tmp_path / 'source'
    (source / 'tests').mkdir(parents=True)
    archive = tmp_path / 'release.zip'
    with zipfile.ZipFile(archive, 'w') as bundle:
        bundle.writestr('package/install.py', '')
    case = dict(profile, imports=[], allowed_skips=[], release=dict(
        requires_python='>=3.10', requires_weewx='>=5', archive=dict(
            url=archive.as_uri(), format='zip',
            sha256=hashlib.sha256(archive.read_bytes()).hexdigest())))

    def reject_unsupported_installer(args, **kwargs):
        if str(CI / 'installed_files.py') in args:
            raise ValueError('Destinations outside repository-managed roots')

    monkeypatch.setattr(compat, 'command', reject_unsupported_installer)
    work = tmp_path / 'work'
    assert compat.run(case, source, work) == 1
    result = json.loads((work / 'result.json').read_text())
    assert result['status'] == 'failed'
    assert result['phase'] == 'installed files'
    assert result['details'] == ['Destinations outside repository-managed roots']


@pytest.fixture
def issue_cases():
    """Supply a complete pair of checks for one package."""
    return [dict(package='example', branch=branch, python='3.14', weewx_sha='abc123',
                 weewx_repository='weewx-packages/weewx',
                 repository='owner/example', source_sha='release-sha',
                 release={'version': '1.0', 'archive': {'url': 'https://example.test/release.zip'}})
            for branch in ['master', 'development']]


def result_set(cases, states):
    """Build results with named states for issue lifecycle tests."""
    return {issues.result_name(case): {'status': state, 'phase': 'tests', 'details': ['broken']}
            for case, state in zip(cases, states)}


def bot_issue(state='open', author='github-actions[bot]'):
    """Return an issue carrying the automation marker."""
    return {'number': 42, 'state': state, 'user': {'login': author},
            'body': '<!-- weewx-compatibility:example -->\nOld failure'}


@pytest.mark.parametrize('state', ['open', 'closed'])
def test_repeated_failure_reuses_existing_issue(issue_cases, monkeypatch, state):
    api = Mock()
    monkeypatch.setattr(issues, 'github', api)
    results = result_set(issue_cases, ['passed', 'failed'])
    issues.reconcile(issue_cases, results, [bot_issue(state)], 'owner/catalog', 'https://run/1')
    assert api.call_count == 1
    assert api.call_args.args[0] == 'repos/owner/catalog/issues/42'
    assert api.call_args.kwargs == {'method': 'PATCH'}
    assert api.call_args.args[1]['state'] == 'open'


def test_human_issue_is_never_edited(issue_cases, monkeypatch):
    api = Mock()
    monkeypatch.setattr(issues, 'github', api)
    issues.reconcile(issue_cases, result_set(issue_cases, ['failed', 'passed']),
                     [bot_issue(author='maintainer')], 'owner/catalog', 'https://run/1')
    assert api.call_args.args[0] == 'repos/owner/catalog/issues'
    assert 'method' not in api.call_args.kwargs


@pytest.mark.parametrize('states', [['passed', 'error'], ['passed'], ['error', 'error']])
def test_incomplete_or_broken_infrastructure_never_closes_issue(issue_cases, monkeypatch, states):
    api = Mock()
    monkeypatch.setattr(issues, 'github', api)
    issues.reconcile(issue_cases, result_set(issue_cases, states), [bot_issue()],
                     'owner/catalog', 'https://run/1')
    api.assert_not_called()


def test_missing_result_cannot_hide_another_confirmed_failure(issue_cases, monkeypatch):
    api = Mock()
    monkeypatch.setattr(issues, 'github', api)
    issues.reconcile(issue_cases, result_set(issue_cases, ['failed']), [],
                     'owner/catalog', 'https://run/1')
    assert api.call_count == 1
    assert 'missing' in api.call_args.args[1]['body']


def test_full_recovery_closes_once(issue_cases, monkeypatch):
    api = Mock()
    monkeypatch.setattr(issues, 'github', api)
    results = result_set(issue_cases, ['passed', 'passed'])
    issues.reconcile(issue_cases, results, [bot_issue()], 'owner/catalog', 'https://run/1')
    assert api.call_args.args[1] == {'state': 'closed', 'state_reason': 'completed'}
    api.reset_mock()
    issues.reconcile(issue_cases, results, [bot_issue('closed')], 'owner/catalog', 'https://run/2')
    api.assert_not_called()


def test_explicit_python_profile_does_not_claim_unsupported_versions(package, monkeypatch):
    monkeypatch.setattr(compat, 'revision', lambda *args: 'a'*40)
    checks = {'example': dict(repository='owner/example', ref='v{version}',
              imports=[], allowed_skips=[], pythons=['3.14'])}
    plan = compat.matrix({'packages': [package]}, checks)
    assert len(plan['include']) == 2
    assert {case['python'] for case in plan['include']} == {'3.14'}
    checks['example']['pythons'] = []
    with pytest.raises(ValueError, match='Python'):
        compat.matrix({'packages': [package]}, checks)


def test_changes_select_only_the_packages_they_affect(tmp_path, monkeypatch):
    def write(path, data):
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data if isinstance(data, str) else json.dumps(data))
        subprocess.run(['git', 'add', '-A'], cwd=tmp_path, check=True)

    packages = [{'id': 'a', 'releases': []}, {'id': 'b', 'releases': []}]
    checks = {'a': {'repository': 'org/a'}, 'b': {'repository': 'org/b'}}
    subprocess.run(['git', 'init', '-q'], cwd=tmp_path, check=True)
    write('repository.json', {'packages': packages})
    write('ci/packages.json', checks)
    write('ci/mirrors.json', [{'fork': 'org/b', 'weekday': 3}])
    subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@example.org',
                    'commit', '-qm', 'base'], cwd=tmp_path, check=True)
    monkeypatch.setattr(compat, 'ROOT', tmp_path)
    released = [dict(packages[0], releases=[{'version': '1.0'}]), packages[1]]
    write('repository.json', {'packages': released})
    write('README.md', 'Generated table')
    assert compat.changed_selection('HEAD', {'packages': released}, checks, {}, 3) == {'a'}
    write('ci/recipes/b/package.patch', 'patch')
    assert compat.changed_selection('HEAD', {'packages': released}, checks, {}, 3) == {'a', 'b'}
    (tmp_path / 'ci/recipes/b/package.patch').unlink()
    # Code can affect every package; the weekday group stands in for all.
    write('ci/compatibility.py', 'changed')
    assert compat.changed_selection('HEAD', {'packages': packages}, checks, {}, 3) == {'b'}


def test_release_requirements_become_test_dependencies():
    check = {'repository': 'org/a', 'pip_packages': ['pytest-mock'], 'system_packages': ['tzdata']}
    release = {'requirements': {'python': ['numpy'], 'debian': ['python3-numpy', 'librtlsdr0']}}
    merged = compat.with_release_requirements(check, release)
    assert merged['pip_packages'] == ['pytest-mock', 'numpy']
    # The tests run in their own Python, so Debian's numpy is not installed.
    assert merged['system_packages'] == ['tzdata', 'librtlsdr0']
    assert check['pip_packages'] == ['pytest-mock']
