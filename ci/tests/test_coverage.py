"""Keep every tracked source visible, including failed or incomplete installations."""

import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('project_coverage', Path(__file__).parents[1] / 'project_coverage.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def test_component_coverage_is_explicit_and_does_not_hide_unassigned_repository():
    mirrors = [dict(fork='org/complete', weekday=1), dict(fork='org/blocked', weekday=2),
               dict(fork='org/missing', weekday=3)]
    packages = {'complete': dict(repository='org/complete')}
    external = {'partial': dict(check_profile=dict(repository='org/blocked', coverage='component'))}
    with pytest.raises(ValueError, match='org/missing'):
        checks.coverage(mirrors, packages, external)
    rows = checks.coverage(mirrors[:2], packages, external)
    assert rows[0]['checks'][0]['coverage'] == 'component'
    assert rows[1]['checks'][0]['coverage'] == 'release'
    assert {row['repository'] for row in rows} == {'org/blocked', 'org/complete'}


def test_unknown_source_cannot_claim_tracked_coverage():
    with pytest.raises(ValueError, match='no tracked source'):
        checks.coverage([], {'wrong': dict(repository='org/wrong')}, {})


def test_real_registries_keep_every_tracked_source_under_ci():
    root = Path(__file__).resolve().parents[2]
    mirrors = json.loads((root / 'ci/mirrors.json').read_text())
    packages = json.loads((root / 'ci/packages.json').read_text())
    external = json.loads((root / 'ci/external.json').read_text())
    rows = checks.coverage(mirrors, packages, external)
    assert {row['repository'] for row in rows} == {mirror['fork'] for mirror in mirrors}
    for row in rows:
        for profile in row['checks']:
            if profile['tests_path'] != 'source/tests':
                assert list((root / profile['tests_path']).glob('test_*.py')), row['repository']
