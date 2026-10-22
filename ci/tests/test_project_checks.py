"""Reject coverage gaps and source files that conceal broken release payloads."""

import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import Mock
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import compatibility as compat


def test_large_plan_preserves_every_case_and_keeps_profiles_in_artifact():
    cases = [dict(package='project-%s' % (number // 4), branch='master', python='3.14',
                  repository='owner/project', source_sha='source', weewx_repository='owner/core',
                  weewx_sha='core', release={'archive': {'url': 'x' * 5000}})
             for number in range(508)]
    groups = compat.shards({'include': cases})['include']
    assert [len(group['cases']['include']) for group in groups] == [200, 200, 108]
    flattened = [case for group in groups for case in group['cases']['include']]
    assert [cases[case['case_id']]['package'] for case in flattened] == [case['package'] for case in cases]
    assert {case['case_id'] for case in flattened} == set(range(508))
    assert 'release' not in flattened[0]
    assert len(json.dumps(groups).encode('utf-16-le')) < 1024 * 1024


@pytest.mark.parametrize('limit', [0, 257])
def test_invalid_group_size_cannot_bypass_github_limit(limit):
    with pytest.raises(ValueError, match='group size'):
        compat.shards({'include': []}, limit)


@pytest.mark.parametrize('packages', [['--allow-unauthenticated'], ['php-cli;id'], ['$(id)'],
                                     ['php-cli\nmalicious'], 'php-cli', [None]])
def test_system_dependencies_cannot_supply_commands_or_options(packages):
    with pytest.raises(ValueError, match='system package'):
        compat.system_packages({'system_packages': packages})


def test_external_project_gets_both_core_branches_without_becoming_catalog_package(monkeypatch):
    monkeypatch.setattr(compat, 'revision', Mock(side_effect=lambda repo, ref: repo + '/' + ref))
    external = {'wordpress': dict(release={'version': '1.0'}, check_profile=dict(
        repository='owner/wp', ref='pinned', imports=[], allowed_skips=[], system_packages=['php-cli']))}
    plan = compat.matrix({'packages': []}, {}, external)
    assert len(plan['include']) == 4
    assert {case['kind'] for case in plan['include']} == {'external'}
    assert {case['branch'] for case in plan['include']} == {'master', 'development'}


@pytest.fixture
def project(tmp_path, monkeypatch):
    """Give pytest an archive and a separate, deliberately misleading source tree."""
    root = tmp_path / 'catalog'
    tests = root / 'ci/project_tests/example'
    tests.mkdir(parents=True)
    fixtures = Path(compat.ROOT / 'ci/project_tests/conftest.py').read_text()
    (tests.parent / 'conftest.py').write_text(fixtures)
    (tests / 'test_payload.py').write_text('''def test_actual_release(payload, station, case):
    import importlib.util
    spec = importlib.util.spec_from_file_location('payload_code', payload / 'module.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.answer == 42
    assert station.name == 'station'
    assert case['package'] == 'example'
''')
    source = tmp_path / 'source'
    source.mkdir()
    (source / 'module.py').write_text('answer = 42\n')
    archive = tmp_path / 'release.zip'
    with zipfile.ZipFile(archive, 'w') as bundle:
        bundle.writestr('package/install.py', '')
        bundle.writestr('package/module.py', 'answer = 13\n')
        # This regular package would hide installed station modules if the
        # import phase prepended payload/bin to PYTHONPATH.
        bundle.writestr('package/bin/user/__init__.py', '')
    case = dict(package='example', tests_path='ci/project_tests/example', imports=[], allowed_skips=[],
                release=dict(requires_python='>=3.10', requires_weewx='>=5', version='1.0', archive=dict(
                    url=archive.as_uri(), format='zip', sha256=hashlib.sha256(archive.read_bytes()).hexdigest())))
    monkeypatch.setattr(compat, 'ROOT', root)
    monkeypatch.setitem(sys.modules, 'weewx', Mock(__version__='5.6.0'))
    return source, case


def test_central_tests_read_archive_even_with_fixed_checkout_and_no_source_tests(project, tmp_path, monkeypatch):
    source, case = project
    recorded = []
    real_command = compat.command

    def execute(args, cwd=None, env=None, input_text=None):
        recorded.append((args, dict(env or {})))
        if 'pytest' in args:
            real_command(args, cwd=cwd, env=env, input_text=input_text)

    monkeypatch.setattr(compat, 'command', execute)
    work = tmp_path / 'work'
    assert compat.run(case, source, work) == 1
    result = json.loads((work / 'result.json').read_text())
    assert result['status'] == 'failed'
    assert any('13 == 42' in detail for detail in result['details'])
    imported = next(env for args, env in recorded if '-c' in args)
    assert imported['PYTHONPATH'] == str(work / 'station/bin')
    assert not (work / 'payload/package/tests').exists()


def test_external_archive_needs_no_installer_and_never_runs_weectl(project, tmp_path, monkeypatch):
    source, case = project
    archive = tmp_path / 'external.zip'
    with zipfile.ZipFile(archive, 'w') as bundle:
        bundle.writestr('package/module.py', 'answer = 42\n')
    case.update(kind='external', initialize_archive=True)
    case['release']['archive'].update(url=archive.as_uri(), sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
    real_command = compat.command

    def execute(args, cwd=None, env=None, input_text=None):
        assert args[0] != 'weectl'
        assert 'weewx.manager' not in ' '.join(args)
        return real_command(args, cwd=cwd, env=env, input_text=input_text)

    monkeypatch.setattr(compat, 'command', execute)
    assert compat.run(case, source, tmp_path / 'work') == 0


def test_prerequisite_failure_is_infrastructure_not_extension_failure(project, tmp_path, monkeypatch):
    source, case = project
    case['install_prerequisites'] = [dict(repository='owner/prerequisite', sha='a' * 40)]

    def execute(args, cwd=None, env=None, input_text=None):
        if args[0] == 'git':
            raise OSError('prerequisite unreachable')

    monkeypatch.setattr(compat, 'command', execute)
    assert compat.run(case, source, tmp_path / 'work') == 1
    result = json.loads((tmp_path / 'work/result.json').read_text())
    assert result['status'] == 'error'
    assert result['phase'] == 'prerequisites'
    assert result['details'] == ['prerequisite unreachable']


def test_project_test_path_cannot_escape_registry(project, tmp_path, monkeypatch):
    source, case = project
    case['tests_path'] = '../source'
    monkeypatch.setattr(compat, 'command', Mock())
    assert compat.run(case, source, tmp_path / 'work') == 1
    result = json.loads((tmp_path / 'work/result.json').read_text())
    assert any('under ci/project_tests' in detail for detail in result['details'])
