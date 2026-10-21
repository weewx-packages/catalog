"""Package immutable upstream releases without changing mirrored source trees.

The build and test jobs receive read-only credentials. The publishing job reads
receipts and archives but never imports an upstream installer or Python module.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

from packaging.version import InvalidVersion, Version

from compatibility import BRANCHES, PYTHONS, ROOT, WEEWX_REPOSITORY, github, revision


def version(tag, prefix):
    """Normalize a known upstream tag, excluding development releases.

    Args:
        tag (str): Original Git tag.
        prefix (str): Project-specific tag prefix.

    Returns:
        str|None: Stable version, or None for another tag convention or prerelease.
    """
    if not tag.startswith(prefix):
        return None
    try:
        parsed = Version(tag[len(prefix):].lstrip('.'))
    except InvalidVersion:
        return None
    return None if parsed.is_prerelease or parsed.is_devrelease else str(parsed)


def plan(specs, catalog):
    """Find stable releases newer than the catalog and pin all test revisions.

    Args:
        specs (list[dict]): Trusted upstream definitions and test profiles.
        catalog (dict): Current published catalog.

    Returns:
        dict: Candidate packages and a complete compatibility matrix.
    """
    commits = {branch: revision(WEEWX_REPOSITORY, branch) for branch in BRANCHES}
    candidates, cases = [], []
    for spec in specs:
        releases = github('repos/%s/releases?per_page=100' % spec['upstream'])
        if spec.get('tagged_releases'):
            published = {release['tag_name'] for release in releases}
            for tag in github('repos/%s/tags?per_page=100' % spec['upstream']):
                if tag['name'] not in published:
                    releases.append(dict(tag_name=tag['name'], draft=False, prerelease=False,
                        assets=[], html_url='https://github.com/%s/releases/tag/%s' %
                        (spec['upstream'], tag['name'])))
        releases = [r for r in releases if not r['draft'] and not r['prerelease']
                    and version(r['tag_name'], spec['tag_prefix']) is not None]
        if not releases:
            raise ValueError('No stable upstream release: ' + spec['upstream'])
        latest = max(releases, key=lambda r: Version(version(r['tag_name'], spec['tag_prefix'])))
        selected = version(latest['tag_name'], spec['tag_prefix'])
        installed = next((p for p in catalog['packages'] if p['id'] == spec['id']), None)
        if installed and any(Version(r['version']) >= Version(selected) for r in installed['releases']):
            continue
        sha = revision(spec['fork'], latest['tag_name'])
        if sha != revision(spec['upstream'], latest['tag_name']):
            raise ValueError('Fork tag differs from upstream: ' + latest['tag_name'])
        assets = [a for a in latest['assets'] if a['name'].endswith(('.zip', '.tar.gz'))]
        asset = next((a for a in assets if a['name'].startswith(spec['upstream'].split('/')[1])), None)
        candidate = dict(package=spec['id'], version=selected, tag=latest['tag_name'],
                         source_sha=sha, upstream_release=latest['html_url'],
                         asset=asset['browser_download_url'] if asset else None)
        candidates.append(candidate)
        for branch, commit in commits.items():
            for python in spec['check'].get('pythons', PYTHONS):
                cases.append(dict(package=spec['id'], branch=branch, python=python,
                    weewx_repository=WEEWX_REPOSITORY, weewx_sha=commit,
                    source_sha=sha, repository=spec['fork']))
    return {'candidates': candidates, 'matrix': {'include': cases}}


def package(spec, candidate, source, output):
    """Copy an upstream release asset or archive its exact tagged tree.

    Args:
        spec (dict): Trusted definition of this package.
        candidate (dict): Pinned upstream release.
        source (Path): Git checkout containing the pinned source commit.
        output (Path): Directory for the archive and provenance receipt.

    Returns:
        dict: Receipt binding package, upstream commit and archive digest.
    """
    output.mkdir(parents=True, exist_ok=True)
    suffix = '.tar.gz' if candidate['asset'] and candidate['asset'].endswith('.tar.gz') else '.zip'
    archive = output / ('%s-%s%s' % (spec['id'], candidate['version'], suffix))
    if candidate['asset']:
        with urllib.request.urlopen(candidate['asset'], timeout=60) as response:
            archive.write_bytes(response.read())
    else:
        with archive.open('wb') as stream:
            subprocess.run(['git', '-C', str(source), 'archive', '--format=zip',
                '--prefix=%s-%s/' % (spec['id'], candidate['version']), candidate['source_sha']],
                stdout=stream, check=True)
    receipt = dict(candidate, filename=archive.name,
                   sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                   format='tar' if suffix == '.tar.gz' else 'zip')
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def compatibility_case(spec, receipt, archive, branch, python, weewx_sha):
    """Build the ordinary compatibility runner's case for a candidate archive.

    Args:
        spec (dict): Trusted package definition.
        receipt (dict): Archive provenance from the build job.
        archive (Path): Downloaded candidate archive.
        branch (str): WeeWX branch under test.
        python (str): Python minor version under test.
        weewx_sha (str): Pinned WeeWX commit.

    Returns:
        dict: Test case using the archive's local URL and recorded checksum.
    """
    return dict(spec['check'], package=spec['id'], installer_name=spec['installer_name'],
        source_sha=receipt['source_sha'], branch=branch, python=python,
        weewx_sha=weewx_sha, weewx_repository=WEEWX_REPOSITORY,
        release={'version': receipt['version'], 'requires_python': spec['requires_python'],
            'requires_weewx': spec['requires_weewx'], 'archive': {
                'url': archive.resolve().as_uri(), 'format': receipt['format'], 'sha256': receipt['sha256']}})


def update_readme(catalog, path, check=False):
    """Generate the package table from the same metadata used by WeeWX clients.

    Args:
        catalog (dict): Complete package index, including manual entries.
        path (Path): README with explicit package-table markers.
        check (bool): Raise instead of writing if the generated table differs.
    """
    text = path.read_text()
    start, end = '<!-- packages:start -->', '<!-- packages:end -->'
    before, table = text.split(start)
    _, after = table.split(end)
    rows = ['| Package | ID | Purpose |', '|---|---|---|']
    for package in catalog['packages']:
        name = package['name'].replace('|', r'\|').replace('\n', ' ')
        description = package['description'].replace('|', r'\|').replace('\n', ' ')
        rows.append('| [%s](%s) | `%s` | %s |' %
                    (name, package['homepage'], package['id'], description))
    replacement = before + start + '\n' + '\n'.join(rows) + '\n' + end + after
    if check and replacement != text:
        raise ValueError('README package table is stale; run python ci/upstreams.py readme')
    if not check:
        path.write_text(replacement)


def publish(specs, plan_data, artifacts):
    """Publish tested archives and update catalog metadata without executing them.

    Args:
        specs (list[dict]): Definitions from the trusted catalog checkout.
        plan_data (dict): Candidate plan from the planning job.
        artifacts (Path): Downloaded receipts, archives and test results.
    """
    catalog_path, checks_path = ROOT / 'repository.json', ROOT / 'ci/packages.json'
    catalog, checks = json.loads(catalog_path.read_text()), json.loads(checks_path.read_text())
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
        expected = {(branch, python) for branch in BRANCHES
                    for python in spec['check'].get('pythons', PYTHONS)}
        selected_cases = [case for case in plan_data['matrix']['include'] if case['package'] == spec['id']]
        if {(case['branch'], case['python']) for case in selected_cases} != expected:
            raise ValueError('Candidate matrix is incomplete')
        for case in selected_cases:
            if case['package'] == spec['id']:
                result = artifacts / ('candidate-result-%s-%s-%s' %
                                      (spec['id'], case['branch'], case['python'])) / 'result.json'
                if json.loads(result.read_text())['status'] != 'passed':
                    raise ValueError('Candidate has an unsuccessful compatibility case')
        tag = '%s/v%s' % (spec['id'], receipt['version'])
        endpoint = 'repos/weewx-packages/catalog/releases/tags/' + tag.replace('/', '%2F')
        # A failed metadata push can leave a complete release. Reuse its bytes
        # on retry, and refuse replacement even if the version still matches.
        existing = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True)
        if existing.returncode:
            body = 'Package from %s at %s (%s).\n\nSource is unchanged. Tested against WeeWX master and development.' % (
                spec['upstream'], receipt['tag'], receipt['source_sha'])
            notes = folder / 'release-notes.txt'
            notes.write_text(body + '\n')
            subprocess.run(['gh', 'release', 'create', tag, str(archive), str(folder / 'receipt.json'),
                '--repo', 'weewx-packages/catalog', '--title', spec['name'] + ' ' + receipt['version'],
                '--notes-file', str(notes), '--latest=false'], check=True)
        else:
            release = json.loads(existing.stdout)
            asset = next(a for a in release['assets'] if a['name'] == archive.name)
            if asset.get('digest') != 'sha256:' + receipt['sha256']:
                raise ValueError('Published release bytes differ; use a new version')
        url = 'https://github.com/weewx-packages/catalog/releases/download/%s/%s' % (tag, archive.name)
        entry = next((p for p in catalog['packages'] if p['id'] == spec['id']), None)
        if entry is None:
            entry = dict(id=spec['id'], installer_name=spec['installer_name'], name=spec['name'],
                description=spec['description'], types=['skin'], keywords=[spec['id'], 'skin', 'charts', 'weather'],
                homepage='https://github.com/' + spec['fork'], releases=[])
            catalog['packages'].append(entry)
        if not any(r['version'] == receipt['version'] for r in entry['releases']):
            entry['releases'].append(dict(version=receipt['version'], requires_python=spec['requires_python'],
                requires_weewx=spec['requires_weewx'], archive=dict(url=url, format=receipt['format'],
                sha256=receipt['sha256']), release_notes=receipt['upstream_release'], restart_required=True))
        checks[spec['id']] = dict(spec['check'], ref=receipt['source_sha'])
    catalog_path.write_text(json.dumps(catalog, indent=2) + '\n')
    checks_path.write_text(json.dumps(checks, indent=2) + '\n')
    update_readme(catalog, ROOT / 'README.md')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'package', 'publish', 'readme'])
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--candidate')
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--plan', type=Path)
    args = parser.parse_args()
    specs = json.loads((ROOT / 'ci/upstreams.json').read_text())
    if args.action == 'plan':
        print(json.dumps(plan(specs, json.loads((ROOT / 'repository.json').read_text()))))
    elif args.action == 'package':
        candidate = json.loads(args.candidate)
        spec = next(s for s in specs if s['id'] == candidate['package'])
        package(spec, candidate, args.source, args.output)
    elif args.action == 'readme':
        update_readme(json.loads((ROOT / 'repository.json').read_text()), ROOT / 'README.md', args.check)
    else:
        publish(specs, json.loads(args.plan.read_text()), args.output)
