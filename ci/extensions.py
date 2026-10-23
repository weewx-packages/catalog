"""Package new versions of mirrored extensions that publish no tags or releases.

Most extension authors bump a version constant in their installer and nothing
else. The upstream skins workflow keys on tags and releases, so it cannot see
these. This module reads the version from the mirrored source, packages the
exact commit (plus an optional catalog patch) and publishes it after the
compatibility matrix passes. Like ci/upstreams.py, it never imports upstream
Python in a job with write access.
"""

import argparse
import base64
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile

from packaging.version import InvalidVersion, Version

from compatibility import BRANCHES, PYTHONS, ROOT, WEEWX_REPOSITORY, github, revision
from upstreams import compatibility_case, update_listing  # noqa: F401  (re-exported for the workflow)

SPECS = ROOT / 'ci/upstream-extensions.json'


def source_version(text, spec):
    """Read a version string from source text without executing it.

    Args:
        text (str): Contents of the file that declares the version.
        spec (dict): Trusted definition with `version_regex`, whose first group
            captures the version. Optional `version_sub` pairs rewrite it to
            PEP 440, and `letter_post` turns a trailing letter into `.postN`.

    Returns:
        str: Normalized PEP 440 version.

    Raises:
        ValueError: The pattern does not match, or the match is not a version.
    """
    match = re.search(spec['version_regex'], text, re.M)
    if not match:
        raise ValueError('No version found with pattern ' + spec['version_regex'])
    raw = match.group(1).strip()
    for pattern, replacement in spec.get('version_sub', []):
        raw = re.sub(pattern, replacement, raw)
    if spec.get('letter_post'):
        raw = re.sub(r'([a-z])$', lambda letter: '.post%d' % (ord(letter.group(1)) - 96), raw)
    try:
        return str(Version(raw))
    except InvalidVersion as error:
        raise ValueError('Not a PEP 440 version: ' + raw) from error


def package_version(spec, upstream_version):
    """Return the catalog version, adding a post-release for catalog patches.

    Args:
        spec (dict): Trusted package definition.
        upstream_version (str): Version declared by the source.

    Returns:
        str: Version with `.postN` appended if the spec carries a patch.
    """
    return upstream_version + '.post%d' % spec['post'] if spec.get('patch') else upstream_version


def newest_published(package):
    """Find the highest version the catalog already lists, yanked or not.

    Args:
        package (dict|None): Catalog entry, or None before the first release.

    Returns:
        Version|None: Highest listed version.
    """
    if package is None or not package['releases']:
        return None
    return max(Version(release['version']) for release in package['releases'])


def plan(specs, catalog):
    """Find upstream versions newer than the catalog and pin all test revisions.

    Args:
        specs (list[dict]): Trusted definitions and test profiles.
        catalog (dict): Current published catalog.

    Returns:
        dict: Candidate packages and a complete compatibility matrix.
    """
    commits = {branch: revision(WEEWX_REPOSITORY, branch) for branch in BRANCHES}
    candidates, cases = [], []
    for spec in specs:
        if spec.get('blocked'):
            continue
        sha = revision(spec['fork'], spec['branch'])
        entry = github('repos/%s/contents/%s?ref=%s' % (spec['fork'], spec['version_file'], sha))
        text = base64.b64decode(entry['content']).decode('utf-8')
        upstream = source_version(text, spec)
        package = next((p for p in catalog['packages'] if p['id'] == spec['id']), None)
        version = package_version(spec, upstream)
        newest = newest_published(package)
        if newest is not None and Version(version) <= newest:
            continue
        candidates.append(dict(package=spec['id'], version=version,
                               upstream_version=upstream, source_sha=sha, tag=spec['branch'],
                               upstream_release='https://github.com/%s/commit/%s' % (spec['upstream'], sha)))
        for branch, commit in commits.items():
            for python in spec['check'].get('pythons', PYTHONS):
                cases.append(dict(package=spec['id'], branch=branch, python=python,
                                  weewx_repository=WEEWX_REPOSITORY, weewx_sha=commit,
                                  source_sha=sha, repository=spec['fork']))
    return {'candidates': candidates, 'matrix': {'include': cases}}


def build_archive(tree, prefix):
    """Write a reproducible gzip tarball of a directory.

    Args:
        tree (Path): Directory whose contents become the archive.
        prefix (str): Single top-level directory inside the archive.

    Returns:
        bytes: Archive bytes. Equal input trees give equal bytes.
    """
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.PAX_FORMAT) as archive:
        for path in sorted(tree.rglob('*')):
            if '.git' in path.relative_to(tree).parts:
                continue
            info = archive.gettarinfo(str(path), arcname=prefix + '/' + path.relative_to(tree).as_posix())
            info.uid = info.gid = 0
            info.uname = info.gname = ''
            info.mtime = 0
            info.mode = 0o755 if path.is_dir() or info.mode & 0o111 else 0o644
            if path.is_file():
                with path.open('rb') as stream:
                    archive.addfile(info, stream)
            else:
                archive.addfile(info)
    return gzip.compress(raw.getvalue(), mtime=0)


def package(spec, candidate, source, output):
    """Archive the exact source commit, applying the catalog patch if any.

    Args:
        spec (dict): Trusted definition of this package.
        candidate (dict): Pinned upstream version.
        source (Path): Bare Git repository containing the pinned commit.
        output (Path): Directory for the archive and provenance receipt.

    Returns:
        dict: Receipt binding package, source commit, patch and archive digest.
    """
    output.mkdir(parents=True, exist_ok=True)
    name = '%s-%s' % (spec['id'], candidate['version'])
    patch_sha = None
    with tempfile.TemporaryDirectory() as work:
        tree = Path(work) / 'tree'
        tree.mkdir()
        tar = subprocess.run(['git', '-C', str(source), 'archive', '--format=tar', candidate['source_sha']],
                             check=True, capture_output=True).stdout
        with tarfile.open(fileobj=io.BytesIO(tar)) as stream:
            stream.extractall(tree, filter='data')
        if spec.get('patch'):
            patch = (ROOT / spec['patch']).read_bytes()
            patch_sha = hashlib.sha256(patch).hexdigest()
            subprocess.run(['patch', '-p1', '--no-backup-if-mismatch', '-s'], cwd=tree, input=patch, check=True)
        data = build_archive(tree, name)
    archive = output / (name + '.tar.gz')
    archive.write_bytes(data)
    receipt = dict(candidate, filename=archive.name, format='tar.gz', sha256=hashlib.sha256(data).hexdigest(),
                   repository=spec['fork'], patch=spec.get('patch'), patch_sha256=patch_sha,
                   license=spec.get('license'), license_evidence=spec.get('license_evidence', []),
                   limitations=spec.get('limitations', []))
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def publish(specs, plan_data, artifacts):
    """Publish tested archives and update catalog metadata without executing them.

    Args:
        specs (list[dict]): Definitions from the trusted catalog checkout.
        plan_data (dict): Candidate plan from the planning job.
        artifacts (Path): Downloaded receipts, archives and test results.
    """
    catalog_path, checks_path = ROOT / 'repository.json', ROOT / 'ci/packages.json'
    mirrors_path, external_path = ROOT / 'ci/mirrors.json', ROOT / 'ci/external.json'
    catalog, checks = json.loads(catalog_path.read_text()), json.loads(checks_path.read_text())
    mirrors, external = json.loads(mirrors_path.read_text()), json.loads(external_path.read_text())
    by_id = {spec['id']: spec for spec in specs}
    for candidate in plan_data['candidates']:
        spec = by_id[candidate['package']]
        folder = artifacts / ('candidate-' + spec['id'])
        receipt = json.loads((folder / 'receipt.json').read_text())
        if any(receipt[key] != candidate[key] for key in candidate):
            raise ValueError('Receipt differs from pinned candidate')
        archive = folder / receipt['filename']
        if archive.parent != folder or hashlib.sha256(archive.read_bytes()).hexdigest() != receipt['sha256']:
            raise ValueError('Archive differs from receipt')
        expected = {(branch, python) for branch in BRANCHES for python in spec['check'].get('pythons', PYTHONS)}
        selected = [case for case in plan_data['matrix']['include'] if case['package'] == spec['id']]
        if {(case['branch'], case['python']) for case in selected} != expected:
            raise ValueError('Candidate matrix is incomplete')
        for case in selected:
            result = artifacts / ('candidate-result-%s-%s-%s' %
                                  (spec['id'], case['branch'], case['python'])) / 'result.json'
            if json.loads(result.read_text())['status'] != 'passed':
                raise ValueError('Candidate has an unsuccessful compatibility case')
        tag = '%s/v%s' % (spec['id'], receipt['version'])
        endpoint = 'repos/weewx-packages/catalog/releases/tags/' + tag.replace('/', '%2F')
        existing = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True)
        if existing.returncode:
            body = 'Archived from %s at %s.\n\nProject checks: WeeWX master/development, Python %s.\n\n' \
                   'See receipt.json for the patch and verification limits.\n' % (
                       spec['fork'], receipt['source_sha'], '/'.join(spec['check'].get('pythons', PYTHONS)))
            notes = folder / 'release-notes.txt'
            notes.write_text(body)
            command = ['gh', 'release', 'create', tag, str(archive), str(folder / 'receipt.json'),
                       '--repo', 'weewx-packages/catalog', '--title', spec['name'] + ' ' + receipt['version'],
                       '--notes-file', str(notes), '--latest=false']
            if Version(receipt['version']).is_prerelease:
                command.append('--prerelease')
            subprocess.run(command, check=True)
        else:
            asset = next(a for a in json.loads(existing.stdout)['assets'] if a['name'] == archive.name)
            if asset.get('digest') != 'sha256:' + receipt['sha256']:
                raise ValueError('Published release bytes differ; use a new version')
        url = 'https://github.com/weewx-packages/catalog/releases/download/%s/%s' % (tag, archive.name)
        entry = next((p for p in catalog['packages'] if p['id'] == spec['id']), None)
        if entry is None:
            entry = dict(id=spec['id'], installer_name=spec['installer_name'], name=spec['name'],
                         description=spec['description'], types=spec['types'], category=spec['category'],
                         homepage='https://github.com/' + spec['fork'], releases=[])
            catalog['packages'].append(entry)
        if not any(r['version'] == receipt['version'] for r in entry['releases']):
            entry['releases'].append(dict(version=receipt['version'], requires_python=spec['requires_python'],
                                          archive=dict(url=url, format='tar.gz', sha256=receipt['sha256']),
                                          requires_weewx=spec['requires_weewx'],
                                          restart_required=spec.get('restart_required', True)))
        checks[spec['id']] = dict(spec['check'], ref=receipt['source_sha'])
        # A released package replaces the source-only check of its mirror.
        external.pop(spec.get('external_source'), None)
        for mirror in mirrors:
            if mirror['fork'] == spec['fork']:
                mirror['check'] = 'catalog'
    mirrors_path.write_text(json.dumps(mirrors, indent=2, ensure_ascii=False) + '\n')
    external_path.write_text(json.dumps(external, indent=2, ensure_ascii=False) + '\n')
    catalog_path.write_text(json.dumps(catalog, indent=2) + '\n')
    checks_path.write_text(json.dumps(checks, indent=2) + '\n')
    update_listing(catalog)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'package', 'publish'])
    parser.add_argument('--candidate')
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--plan', type=Path)
    args = parser.parse_args()
    specs = json.loads(SPECS.read_text())
    if args.action == 'plan':
        print(json.dumps(plan(specs, json.loads((ROOT / 'repository.json').read_text()))))
    elif args.action == 'package':
        candidate = json.loads(args.candidate)
        package(next(s for s in specs if s['id'] == candidate['package']), candidate, args.source, args.output)
    else:
        publish(specs, json.loads(args.plan.read_text()), args.output)
