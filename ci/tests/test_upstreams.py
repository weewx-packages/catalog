"""Reject mutable packages, prereleases and incomplete publication evidence."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import compatibility as compat
import upstreams


@pytest.fixture
def spec():
    return dict(id='example', upstream='author/example', fork='org/example',
        tag_prefix='v', name='Example', installer_name='example', description='A skin',
        requires_python='>=3.10', requires_weewx='>=5,<6', check=dict(
        repository='org/example', ref='v{version}', imports=[], allowed_skips=[], pythons=['3.14']))


@pytest.mark.parametrize('tag,prefix,want', [
    ('v1.2.3','v','1.2.3'), ('ver.1.2.3','ver','1.2.3'), ('1.2.3','','1.2.3'),
    ('v1.2rc1','v',None), ('v1.2.dev1','v',None), ('feature','v',None),
])
def test_tag_versions(tag, prefix, want):
    assert upstreams.version(tag, prefix) == want


def test_candidate_selection_ignores_prereleases_and_older_releases(spec, monkeypatch):
    def release(tag, **kwargs):
        return dict(tag_name=tag, draft=False, prerelease=False, assets=[], html_url='https://release', **kwargs)
    monkeypatch.setattr(upstreams, 'github', lambda _: [release('v1.1'), release('v2.0rc1'), release('v1.2')])
    monkeypatch.setattr(upstreams, 'revision', lambda *args: 'a'*40)
    plan = upstreams.plan([spec], {'packages': []})
    assert plan['candidates'][0]['version'] == '1.2'
    assert len(plan['matrix']['include']) == 2
    assert {c['python'] for c in plan['matrix']['include']} == {'3.14'}
    assert not upstreams.plan([spec], {'packages': [dict(id='example', releases=[{'version':'1.2'}])]})['candidates']


def test_candidate_refuses_unsynchronized_fork(spec, monkeypatch):
    monkeypatch.setattr(upstreams, 'github', lambda _: [dict(tag_name='v1', draft=False,
        prerelease=False, assets=[], html_url='https://release')])
    monkeypatch.setattr(upstreams, 'revision', lambda repo, ref: repo)
    with pytest.raises(ValueError, match='differs'):
        upstreams.plan([spec], {'packages': []})


def test_source_archive_preserves_installer_without_executing_it(spec, tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    subprocess.run(['git','init','-b','main',str(source)], check=True, capture_output=True)
    installer = b'raise RuntimeError("must never execute during packaging")\n'
    (source/'install.py').write_bytes(installer)
    (source/'LICENSE').write_text('original license\n')
    subprocess.run(['git','-C',str(source),'add','.'],check=True)
    subprocess.run(['git','-C',str(source),'-c','user.name=Test','-c','user.email=test@example.test',
                    'commit','-m','Source'],check=True,capture_output=True)
    sha = subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    receipt = upstreams.package(spec,dict(asset=None,version='1.0',source_sha=sha),source,tmp_path/'out')
    with zipfile.ZipFile(tmp_path/'out'/receipt['filename']) as archive:
        assert archive.read('example-1.0/install.py') == installer
        assert archive.read('example-1.0/LICENSE') == b'original license\n'


def test_existing_asset_is_copied_byte_for_byte(spec, tmp_path):
    asset=tmp_path/'original.tar.gz'
    asset.write_bytes(b'upstream release bytes')
    receipt=upstreams.package(spec,dict(asset=asset.as_uri(),version='1.0',source_sha='abc'),
                              tmp_path/'unused',tmp_path/'out')
    assert (tmp_path/'out'/receipt['filename']).read_bytes() == asset.read_bytes()
    assert receipt['sha256'] == hashlib.sha256(asset.read_bytes()).hexdigest()


@pytest.fixture
def publication(spec, tmp_path, monkeypatch):
    monkeypatch.setattr(upstreams,'ROOT',tmp_path)
    (tmp_path/'ci').mkdir()
    (tmp_path/'repository.json').write_text('{"packages": []}')
    (tmp_path/'ci/packages.json').write_text('{}')
    (tmp_path/'README.md').write_text('Intro\n<!-- packages:start -->\nold table\n<!-- packages:end -->\nHelp\n')
    artifacts=tmp_path/'artifacts'
    folder=artifacts/'candidate-example'
    folder.mkdir(parents=True)
    archive=folder/'example-1.0.zip'
    archive.write_bytes(b'archive')
    candidate=dict(package='example',version='1.0',source_sha='a'*40,
                   tag='v1.0',asset=None,upstream_release='https://release')
    receipt=dict(candidate,filename=archive.name,format='zip',sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
    (folder/'receipt.json').write_text(json.dumps(receipt))
    cases=[dict(package='example',branch=branch,python='3.14') for branch in compat.BRANCHES]
    for case in cases:
        directory=artifacts/('candidate-result-example-%s-3.14'%case['branch'])
        directory.mkdir()
        (directory/'result.json').write_text('{"status":"passed"}')
    plan=dict(candidates=[candidate],matrix={'include':cases})
    api=Mock(return_value=subprocess.CompletedProcess([],1,'','not found'))
    monkeypatch.setattr(upstreams.subprocess,'run',api)
    return artifacts,plan,archive,api


def test_publication_rejects_archive_changes(spec, publication):
    artifacts,plan,archive,api=publication
    archive.write_bytes(b'changed')
    with pytest.raises(ValueError,match='differs'):
        upstreams.publish([spec],plan,artifacts)
    api.assert_not_called()


def test_publication_requires_complete_matrix(spec, publication):
    artifacts,plan,archive,api=publication
    plan['matrix']['include'].pop()
    with pytest.raises(ValueError,match='incomplete'):
        upstreams.publish([spec],plan,artifacts)
    api.assert_not_called()


def test_publication_rejects_failed_case(spec, publication):
    artifacts,plan,archive,api=publication
    (artifacts/'candidate-result-example-master-3.14/result.json').write_text('{"status":"failed"}')
    with pytest.raises(ValueError,match='unsuccessful'):
        upstreams.publish([spec],plan,artifacts)
    api.assert_not_called()


def test_publication_keeps_tested_revision_and_digest(spec, publication, tmp_path):
    artifacts,plan,archive,api=publication
    upstreams.publish([spec],plan,artifacts)
    catalog=json.loads((tmp_path/'repository.json').read_text())
    checks=json.loads((tmp_path/'ci/packages.json').read_text())
    assert catalog['packages'][0]['releases'][0]['archive']['sha256']==hashlib.sha256(archive.read_bytes()).hexdigest()
    assert checks['example']['ref']=='a'*40
    assert api.call_args.args[0][:3]==['gh','release','create']


def test_readme_uses_catalog_and_preserves_surrounding_text(tmp_path):
    path = tmp_path / 'README.md'
    path.write_text('Introduction\n<!-- packages:start -->\nOld table\n<!-- packages:end -->\nInstall instructions\n')
    package = dict(id='skin', name='A skin', description='One | two', homepage='https://example.test')
    upstreams.update_readme({'packages': [package]}, path)
    text = path.read_text()
    assert '[A skin](https://example.test) | `skin` | One \\| two' in text
    assert text.startswith('Introduction\n') and text.endswith('Install instructions\n')
    upstreams.update_readme({'packages': []}, path)
    assert '`skin`' not in path.read_text()


def test_readme_check_is_read_only(tmp_path):
    path = tmp_path / 'README.md'
    original = '<!-- packages:start -->old<!-- packages:end -->'
    path.write_text(original)
    with pytest.raises(ValueError, match='stale'):
        upstreams.update_readme({'packages': []}, path, check=True)
    assert path.read_text() == original


def test_tag_releases_can_advance_without_a_github_release(spec, monkeypatch):
    spec['tagged_releases'] = True
    monkeypatch.setattr(upstreams, 'github', lambda path: [{'name':'v1.5'}] if '/tags?' in path else [])
    monkeypatch.setattr(upstreams, 'revision', lambda *args: 'a'*40)
    plan = upstreams.plan([spec], {'packages': []})
    assert plan['candidates'][0]['version'] == '1.5'
    assert plan['candidates'][0]['asset'] is None
