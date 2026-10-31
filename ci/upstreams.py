"""Package immutable upstream releases without changing mirrored source trees.

The build and test jobs receive read-only credentials. The publishing job reads
receipts and archives but never imports an upstream installer or Python module.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shlex
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
        if spec.get('blocked'):
            continue
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


PAGE_FOLDER = 'packages'
PAGE_MARKER = '<!-- Generated from repository.json by ci/upstreams.py readme. Do not edit. -->'
CATALOG_ISSUES = 'https://github.com/weewx-packages/catalog/issues'


def cell(text):
    """Escape text for a single Markdown table cell.

    Args:
        text (str): Plain catalog text.

    Returns:
        str: Text without line breaks or unescaped column separators.
    """
    return text.replace('|', r'\|').replace('\n', ' ')


def current_release(package):
    """Select the release a new installation receives.

    Args:
        package (dict): Catalog package entry.

    Returns:
        dict|None: Newest listed stable release, else the newest listed
            prerelease. None if every release is yanked.
    """
    listed = [release for release in package['releases'] if not release.get('yanked')]
    stable = [release for release in listed if not Version(release['version']).is_prerelease]
    candidates = stable or listed
    return max(candidates, key=lambda release: Version(release['version'])) if candidates else None


def requirements_section(needs):
    """Render the commands that provide a release's requirements.

    Debian packages named python3-* are the distribution's builds of the Python
    requirements. A pip installation of WeeWX gets those from pip instead and
    only the other Debian packages from apt.

    Args:
        needs (dict): The release's requirements, possibly empty.

    Returns:
        list[str]: Markdown lines, empty without requirements.
    """
    if not needs:
        return []
    python = needs.get('python', [])
    debian = needs.get('debian', [])
    other = [name for name in debian if not name.startswith('python3-')]
    lines = ['## Requirements', '']
    if debian:
        lines += ['With WeeWX installed from its Debian or Raspberry Pi OS package:', '',
                  '```shell', 'sudo apt install ' + ' '.join(debian), '```', '']
    if python or other:
        lines += ['With a pip installation of WeeWX, activate its virtual environment first:', '',
                  '```shell']
        if python:
            lines.append('python -m pip install ' + ' '.join(shlex.quote(item) for item in python))
        if other:
            lines.append('sudo apt install ' + ' '.join(other))
        lines += ['```', '']
    return lines


def upstream_repositories():
    """Find the projects whose author maintains the package, not this organization.

    Returns:
        dict: Upstream URL by lowercase fork name (e.g., 'weewx-packages/weewx-nws').
            Independent continuations and our own projects are absent.
    """
    mirrors = json.loads((ROOT / 'ci' / 'mirrors.json').read_text())
    skins = json.loads((ROOT / 'ci' / 'upstreams.json').read_text())
    upstreams = {mirror['fork'].lower(): mirror['upstream'].removesuffix('.git')
                 for mirror in mirrors if mirror['sync']}
    # The skins say sync: false in mirrors.json because the Upstream skins workflow
    # syncs them instead of Extension mirrors. Their authors still maintain them.
    upstreams.update({skin['fork'].lower(): 'https://github.com/' + skin['upstream'] for skin in skins})
    return upstreams


def upstream_of(package, upstreams):
    """Look up the upstream project of a catalog package.

    Args:
        package (dict): Catalog package entry.
        upstreams (dict): Result of upstream_repositories().

    Returns:
        str|None: Upstream URL, or None if this organization maintains the package.
    """
    # A homepage is the fork, on mirrors often with a path into its documentation
    # branch. Only the owner and repository name identify it.
    return upstreams.get('/'.join(package['homepage'].split('/')[3:5]).lower())


def package_page(package, upstream=None):
    """Render the catalog page that package guides link to for installation.

    Package READMEs carry no version numbers or archive URLs. This page is the
    single place where the current release and its install command appear.

    Args:
        package (dict): Catalog package entry.
        upstream (str|None): URL of the project that maintains the package, or
            None if this organization maintains it. Default is None.

    Returns:
        str: Complete Markdown page.
    """
    release = current_release(package)
    # A release that declares its requirements and setup is installed from this
    # page alone; the package guide is then only needed for further settings.
    complete = bool(release and (release.get('requirements') or release.get('setup')))
    lines = [PAGE_MARKER, '', '# ' + package['name'], '', package['description'], '']
    if upstream:
        # Forks of maintained projects have their issues turned off, so without
        # this link a reader of the page has no way to reach the author. Archives
        # may carry a catalog patch, and the author must not get those reports.
        lines += ['The author maintains this project at [%s](%s). Ask for support and report' % (
                      '/'.join(upstream.split('/')[3:5]), upstream),
                  'bugs there. The catalog keeps a backup copy, tests the releases and packages',
                  'them. Report problems with the catalog archive in the',
                  '[catalog issues](%s).' % CATALOG_ISSUES, '']
    lines += ['Package ID `%s`. The [installation and configuration guide](%s) lists its' % (
                  package['id'], package['homepage']),
              'further settings.' if complete else 'dependencies and settings.', '']
    if release is None:
        lines += ['All releases of this package are withdrawn. It cannot be installed from the catalog.', '']
        return '\n'.join(lines)
    prerelease = Version(release['version']).is_prerelease
    lines += ['## Current release', '', '| | |', '|---|---|',
              '| Version | %s%s |' % (release['version'], ' (prerelease)' if prerelease else ''),
              '| WeeWX | `%s` |' % release['requires_weewx'],
              '| Python | `%s` |' % release['requires_python']]
    if release.get('release_notes'):
        lines.append('| Release notes | [%s](%s) |' % (release['version'], release['release_notes']))
    lines.append('')
    restart = ' Then restart WeeWX.' if release.get('restart_required') else ''
    steps = release.get('setup', [])
    lines += requirements_section(release.get('requirements', {}))
    lines += ['## Install with stock WeeWX', '']
    if complete:
        # Commands are shown for a package installation, where WeeWX runs as
        # weewx and its files belong to root.
        lines += ['```shell', 'sudo weectl extension install ' + release['archive']['url'], '```', '',
                  'Add `--config /path/to/weewx.conf` if your station uses another configuration file.']
        if steps:
            lines += ['', '## Set up', '', '```shell']
            for step in steps:
                command = step['command'].replace('{user}', 'weewx')
                lines.append(command + ('    # ' + step['note'] if step.get('note') else ''))
            lines += ['```', '']
        else:
            lines += ['Then restart WeeWX.' if release.get('restart_required') else '', '']
        lines += ['For a pip installation, run `weectl` from its virtual environment without',
                  '`sudo`, and use the account that runs WeeWX instead of `weewx`.', '']
    else:
        lines += ['Install the dependencies named in the guide first. Then use the `weectl`',
                  'of the Python environment running WeeWX:', '',
                  '```shell', 'weectl extension install ' + release['archive']['url'], '```', '',
                  'Add `--config /path/to/weewx.conf` if your station uses another configuration file.',
                  'Complete the configuration described in the guide.' + restart, '']
    lines += ['## Install with the package manager', '',
              'The experimental [package manager](https://github.com/weewx-packages/weewx-package-manager#install)',
              'extension installs by package ID and keeps track of updates. Register this',
              'catalog as `packages` once, as its documentation shows, then run:', '',
              '```shell',
              'python -m user.packages install %s --repo packages%s' % (package['id'], ' --pre' if prerelease else ''),
              'python -m user.packages update %s%s' % (package['installer_name'], ' --pre' if prerelease else ''),
              '```', '',
              'The second command installs a later release when the catalog lists one.']
    if complete:
        lines += ['Both check the requirements, install missing Python packages into a virtual',
                  'environment and print the setup steps. `python -m user.packages requirements %s`'
                  % package['installer_name'],
                  'checks them again later.']
    lines += ['', '## Remove', '',
              '```shell', 'weectl extension uninstall ' + package['installer_name'], '```', '']
    others = [entry for entry in package['releases'] if entry is not release]
    if others:
        lines += ['## Other releases', '',
                  '| Version | WeeWX | Python | Archive |', '|---|---|---|---|']
        for entry in sorted(others, key=lambda entry: Version(entry['version']), reverse=True):
            archive = 'Withdrawn' if entry.get('yanked') else '[Download](%s)' % entry['archive']['url']
            lines.append('| %s | `%s` | `%s` | %s |' % (entry['version'], entry['requires_weewx'],
                                                       entry['requires_python'], archive))
        lines.append('')
    return '\n'.join(lines)


def update_pages(catalog, folder, check=False, upstreams=None):
    """Write one page per package and remove pages of packages no longer listed.

    Args:
        catalog (dict): Complete package index, including manual entries.
        folder (Path): Directory holding only generated package pages.
        check (bool): Raise instead of writing if any page differs.
        upstreams (dict|None): Result of upstream_repositories(). None names no
            upstream on any page. Default is None.
    """
    wanted = {package['id'] + '.md': package_page(package, upstream_of(package, upstreams or {}))
              for package in catalog['packages']}
    existing = {path.name: path.read_text() for path in folder.glob('*.md')} if folder.is_dir() else {}
    if check:
        if existing != wanted:
            raise ValueError('Package pages are stale; run python ci/upstreams.py readme')
        return
    folder.mkdir(exist_ok=True)
    for name in set(existing) - set(wanted):
        (folder / name).unlink()
    for name, text in wanted.items():
        if existing.get(name) != text:
            (folder / name).write_text(text)


CATEGORIES = (('skin', 'Skins'), ('driver', 'Drivers and data sources'), ('uploader', 'Uploaders'),
              ('forecast', 'Forecasts and warnings'), ('other', 'Other'))


def update_readme(catalog, path, check=False):
    """Generate one package table per category from the index used by WeeWX clients.

    Args:
        catalog (dict): Complete package index, including manual entries.
        path (Path): README with explicit package-table markers.
        check (bool): Raise instead of writing if the generated tables differ.
    """
    keys = [key for key, _ in CATEGORIES]
    unknown = sorted({package['category'] for package in catalog['packages']} - set(keys))
    if unknown:
        raise ValueError('Unknown package categories: ' + ', '.join(unknown))
    text = path.read_text()
    start, end = '<!-- packages:start -->', '<!-- packages:end -->'
    before, table = text.split(start)
    _, after = table.split(end)
    rows = []
    for key, title in CATEGORIES:
        members = sorted((package for package in catalog['packages'] if package['category'] == key),
                         key=lambda package: package['name'].lower())
        if not members:
            continue
        rows += ['', '### ' + title, '', '| Package | Install | Purpose |', '|---|---|---|']
        for package in members:
            rows.append('| [%s](%s) | [`%s`](%s/%s.md) | %s |' %
                        (cell(package['name']), package['homepage'], package['id'],
                         PAGE_FOLDER, package['id'], cell(package['description'])))
    replacement = before + start + '\n' + '\n'.join(rows).lstrip('\n') + '\n' + end + after
    if check and replacement != text:
        raise ValueError('README package table is stale; run python ci/upstreams.py readme')
    if not check:
        path.write_text(replacement)


def update_listing(catalog, check=False):
    """Regenerate the README table and every package page from one index.

    Args:
        catalog (dict): Complete package index, including manual entries.
        check (bool): Raise instead of writing if anything generated differs.
    """
    update_readme(catalog, ROOT / 'README.md', check)
    update_pages(catalog, ROOT / PAGE_FOLDER, check, upstream_repositories())


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
                description=spec['description'], types=['skin'], category='skin',
                keywords=[spec['id'], 'skin', 'charts', 'weather'],
                homepage='https://github.com/' + spec['fork'], releases=[])
            catalog['packages'].append(entry)
        if not any(r['version'] == receipt['version'] for r in entry['releases']):
            entry['releases'].append(dict(version=receipt['version'], requires_python=spec['requires_python'],
                requires_weewx=spec['requires_weewx'], archive=dict(url=url, format=receipt['format'],
                sha256=receipt['sha256']), release_notes=receipt['upstream_release'], restart_required=True))
        checks[spec['id']] = dict(spec['check'], ref=receipt['source_sha'])
    catalog_path.write_text(json.dumps(catalog, indent=2) + '\n')
    checks_path.write_text(json.dumps(checks, indent=2) + '\n')
    update_listing(catalog)


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
        update_listing(json.loads((ROOT / 'repository.json').read_text()), args.check)
    else:
        publish(specs, json.loads(args.plan.read_text()), args.output)
