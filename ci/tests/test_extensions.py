"""Version detection, reproducible packaging and publication of mirrored extensions."""

import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import extensions  # noqa: E402

SPEC = dict(id='demo', version_regex=r'^VERSION\s*=\s*"([^"]+)"')


def test_source_version_reads_and_normalizes():
    assert extensions.source_version('VERSION = "0.1.0-rc01"\n', SPEC) == '0.1.0rc1'
    spec = dict(SPEC, version_sub=[['-rc0*(\\d+)([a-z]?)$', 'rc\\1\\2']], letter_post=True)
    assert extensions.source_version('VERSION = "1.0.0-rc03c"\n', spec) == '1.0.0rc3.post3'
    with pytest.raises(ValueError):
        extensions.source_version('nothing here', SPEC)
    with pytest.raises(ValueError):
        extensions.source_version('VERSION = "not a version"\n', SPEC)


def test_patched_packages_get_a_post_release():
    assert extensions.package_version(dict(SPEC, patch='x', post=2), '0.6.7') == '0.6.7.post2'
    assert extensions.package_version(SPEC, '0.6.7') == '0.6.7'


def test_newest_published_ignores_order():
    package = dict(releases=[dict(version='1.0.0'), dict(version='1.10.0'), dict(version='1.9.0')])
    assert str(extensions.newest_published(package)) == '1.10.0'
    assert extensions.newest_published(None) is None


def make_source(tmp_path):
    repo = tmp_path / 'source.git'
    work = tmp_path / 'work'
    (work / 'bin/user').mkdir(parents=True)
    (work / 'install.py').write_text('from six.moves import StringIO\n')
    (work / 'bin/user/demo.py').write_text('print("demo")\n')
    run = lambda *args, cwd=work: subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True)
    run('init', '-q', '-b', 'main')
    run('-c', 'user.name=t', '-c', 'user.email=t@example.org', 'add', '.')
    run('-c', 'user.name=t', '-c', 'user.email=t@example.org', 'commit', '-qm', 'one')
    sha = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=work, check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(['git', 'clone', '-q', '--bare', str(work), str(repo)], check=True)
    return repo, sha


def test_package_applies_patch_and_is_reproducible(tmp_path, monkeypatch):
    repo, sha = make_source(tmp_path)
    patch = tmp_path / 'package.patch'
    patch.write_text('--- a/install.py\n+++ b/install.py\n@@ -1 +1 @@\n'
                     '-from six.moves import StringIO\n+from io import StringIO\n')
    monkeypatch.setattr(extensions, 'ROOT', tmp_path)
    spec = dict(SPEC, fork='weewx-packages/demo', patch='package.patch', post=1)
    candidate = dict(package='demo', version='1.0.post1', source_sha=sha)
    first = extensions.package(spec, candidate, repo, tmp_path / 'one')
    second = extensions.package(spec, candidate, repo, tmp_path / 'two')
    assert first['sha256'] == second['sha256']
    assert first['patch_sha256'] == hashlib.sha256(patch.read_bytes()).hexdigest()
    with tarfile.open(tmp_path / 'one/demo-1.0.post1.tar.gz') as archive:
        names = archive.getnames()
        assert 'demo-1.0.post1/install.py' in names
        text = archive.extractfile('demo-1.0.post1/install.py').read().decode()
    assert text == 'from io import StringIO\n'


def test_build_archive_has_one_top_level_directory(tmp_path):
    (tmp_path / 'a').mkdir()
    (tmp_path / 'a/x.txt').write_text('x')
    data = extensions.build_archive(tmp_path, 'pkg-1')
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        assert {name.split('/')[0] for name in archive.getnames()} == {'pkg-1'}


def test_specs_are_complete():
    specs = json.loads(extensions.SPECS.read_text())
    mirrors = {m['fork']: m for m in json.loads((extensions.ROOT / 'ci/mirrors.json').read_text())}
    for spec in specs:
        assert spec['fork'] in mirrors, spec['id']
        assert mirrors[spec['fork']]['weekday'] == spec['weekday'], spec['id']
        assert not spec['check'].get('system_packages'), spec['id']
        if spec.get('patch'):
            assert (extensions.ROOT / spec['patch']).is_file(), spec['id']
