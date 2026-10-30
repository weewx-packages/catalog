"""Test catalog release archives with tests from their pinned source revisions.

The workflow installs WeeWX and pytest before calling ``run``. Downloads and
checksum failures are infrastructure errors; installation, import and test
failures are compatibility failures. Only the latter produce package issues.
"""

import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

from packaging.specifiers import SpecifierSet
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]
WEEWX_REPOSITORY = 'weewx-packages/weewx'
BRANCHES = ('master', 'development')
PYTHONS = ('3.10', '3.14')


def github(path, data=None, method=None):
    """Call the GitHub API using gh's authentication.

    Args:
        path (str): API path, relative to api.github.com.
        data (dict|None): JSON request body, or None for a bodyless request.
        method (str|None): HTTP method, or gh's default.

    Returns:
        dict|list: Decoded JSON response.
    """
    command = ['gh', 'api', path]
    if method:
        command.extend(['--method', method])
    if data is not None:
        command.extend(['--input', '-'])
    result = subprocess.run(command, input=json.dumps(data) if data is not None else None,
                            text=True, capture_output=True, check=True, timeout=60)
    return json.loads(result.stdout)


def latest_release(package, pre=False):
    """Select the newest non-yanked release under an explicit prerelease policy.

    Args:
        package (dict): A catalog package with its releases.
        pre (bool): Include prereleases. Default is False.

    Returns:
        dict: The selected release.
    """
    return max((r for r in package['releases']
                if not r.get('yanked') and (pre or not Version(r['version']).is_prerelease)),
               key=lambda r: Version(r['version']))


def revision(repository, ref):
    """Resolve a GitHub source ref to its immutable commit SHA.

    Args:
        repository (str): GitHub owner/repository.
        ref (str): Branch, tag or commit to resolve.

    Returns:
        str: Full commit SHA.
    """
    response = github('repos/%s/commits/%s' % (repository, ref))
    if not isinstance(response, dict):
        raise ValueError('Expected a GitHub commit object')
    return response['sha']


def matrix(catalog, checks, external=None, selected=None):
    """Resolve one immutable test case per package, WeeWX branch and Python.

    Args:
        catalog (dict): The published package catalog.
        checks (dict): Test source, imports and permitted skips by package ID.
        external (dict|None): Non-catalog projects with a release and check_profile.
        selected (set[str]|None): Package IDs to run, or None for all projects.

    Returns:
        dict: GitHub Actions matrix with an ``include`` list.

    Raises:
        ValueError: A package has no check, or a check has no package.
    """
    package_ids = [p['id'] for p in catalog['packages']]
    if len(set(package_ids)) != len(package_ids) or set(package_ids) != set(checks):
        raise ValueError('Every catalog package needs exactly one entry in ci/packages.json')
    for package in catalog['packages']:
        if any(Version(release['version']).local for release in package['releases']):
            raise ValueError('Catalog versions must not contain local version labels: ' + package['id'])
    external = external or {}
    if set(external) & set(checks):
        raise ValueError('External project IDs must not collide with catalog packages')
    packages = catalog['packages'] + [dict(id=name, installer_name=name, releases=[item['release']])
                                      for name, item in external.items()]
    checks = dict(checks, **{name: dict(item['check_profile'], kind=item['check_profile'].get('kind', 'external'))
                            for name, item in external.items()})
    upstream = {branch: revision(WEEWX_REPOSITORY, branch)
                for branch in BRANCHES}
    cases = []
    for package in packages:
        if selected is not None and package['id'] not in selected:
            continue
        check = checks[package['id']]
        release = (external[package['id']]['release'] if package['id'] in external
                   else latest_release(package, check.get('allow_prereleases', False)))
        check = with_release_requirements(check, release)
        system_packages(check)
        for dependency in check.get('pip_packages', []):
            if canonicalize_name(Requirement(dependency).name) == 'weewx':
                raise ValueError('Package dependencies must not replace the WeeWX checkout')
        ref = check['ref'].format(version=release['version'])
        source_sha = revision(check['repository'], ref)
        if check.get('source_archive'):
            # Source-only checks follow a branch, so their archive and checksum
            # must be resolved together with that branch's immutable commit.
            url = 'https://github.com/%s/archive/%s.zip' % (check['repository'], source_sha)
            with urllib.request.urlopen(url, timeout=60) as response:
                digest = hashlib.sha256(response.read()).hexdigest()
            release = dict(release, version='source ' + source_sha[:12],
                           archive=dict(url=url, format='zip', sha256=digest))
        for branch, weewx_sha in upstream.items():
            pythons = check.get('pythons', PYTHONS)
            if not pythons or not set(pythons).issubset(PYTHONS):
                raise ValueError('Invalid Python test versions for ' + package['id'])
            for python in pythons:
                cases.append(dict(package=package['id'], installer_name=package['installer_name'],
                                  release=release, **check, source_sha=source_sha,
                                  branch=branch, weewx_sha=weewx_sha,
                                  weewx_repository=WEEWX_REPOSITORY, python=python))
    return {'include': cases}


def with_release_requirements(check, release):
    """Add the requirements a release declares to the dependencies of its check.

    The tests run in their own Python, not in Debian's, so Debian packages of
    Python modules (python3-*) are left to the release's pip requirements.

    Args:
        check (dict): Check profile from ci/packages.json.
        release (dict): Selected catalog release.

    Returns:
        dict: A copy of the profile with the release's requirements added.
    """
    needs = release.get('requirements', {})
    check = dict(check)
    check['pip_packages'] = list(check.get('pip_packages', [])) + [
        item for item in needs.get('python', []) if item not in check.get('pip_packages', [])]
    check['system_packages'] = list(check.get('system_packages', [])) + [
        name for name in needs.get('debian', [])
        if not name.startswith('python3-') and name not in check.get('system_packages', [])]
    return check


def changed_selection(base, catalog, checks, external, weekday):
    """Select the packages a change since base can affect.

    A package is selected when its catalog entry, its check profile, its
    recipe or its project tests changed. A change anywhere else, such as the
    CI code or a workflow, can affect every package; it adds the packages of
    the weekday group, the same share a scheduled run tests.

    Args:
        base (str): Git revision to compare the working tree against.
        catalog (dict): Current repository.json.
        checks (dict): Current ci/packages.json.
        external (dict): Current ci/external.json.
        weekday (int): Weekday group, 1 to 5, used for changes outside the data.

    Returns:
        set[str]: Package IDs to test. Empty if nothing that is tested changed.
    """
    def at_base(path, default):
        result = subprocess.run(['git', 'show', '%s:%s' % (base, path)], cwd=ROOT,
                                capture_output=True, text=True)
        return json.loads(result.stdout) if result.returncode == 0 else default

    old_packages = {package['id']: package for package in at_base('repository.json', {}).get('packages', [])}
    old_checks = at_base('ci/packages.json', {})
    old_external = at_base('ci/external.json', {})
    selected = {package['id'] for package in catalog['packages']
                if old_packages.get(package['id']) != package
                or old_checks.get(package['id']) != checks.get(package['id'])}
    selected |= {name for name, item in external.items() if old_external.get(name) != item}
    profiles = dict(checks, **{name: item['check_profile'] for name, item in external.items()})
    changed = subprocess.run(['git', 'diff', '--name-only', base, '--'], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.split()
    for path in changed:
        parts = path.split('/')
        if parts[:2] == ['ci', 'recipes'] and len(parts) > 3:
            selected.add(parts[2])
        elif parts[:2] == ['ci', 'project_tests'] and len(parts) > 3:
            tests_path = '/'.join(parts[:3])
            selected |= {name for name, profile in profiles.items()
                         if profile.get('tests_path', '').rstrip('/') == tests_path}
        elif parts[0] != 'schemas' and path.endswith(('.json', '.md')):
            # Data and documentation. Entries that are tested were compared above.
            continue
        else:
            selected |= weekday_selection(profiles, weekday)
    return selected & set(profiles)


def weekday_selection(profiles, weekday):
    """Return the package IDs whose repository belongs to a weekday group.

    Args:
        profiles (dict): Check profiles by package ID.
        weekday (int): Weekday group, 1 to 5.

    Returns:
        set[str]: Package IDs of that group.
    """
    mirrors = json.loads((ROOT / 'ci/mirrors.json').read_text())
    repositories = {item['fork'] for item in mirrors if item['weekday'] == weekday}
    return {name for name, profile in profiles.items() if profile['repository'] in repositories}


def shards(plan, limit=200):
    """Split a plan into reusable workflow calls below GitHub's 256-job limit.

    Args:
        plan (dict): Full matrix saved in the plan artifact.
        limit (int): Maximum cases in each child matrix, from 1 to 256.

    Returns:
        dict: Matrix of groups containing only checkout fields and a plan index.
    """
    if not 1 <= limit <= 256:
        raise ValueError('Matrix group size must be between 1 and 256')
    fields = ('package', 'branch', 'python', 'repository', 'source_sha',
              'weewx_repository', 'weewx_sha')
    cases = [dict({field: case[field] for field in fields}, case_id=number)
             for number, case in enumerate(plan['include'])]
    return {'include': [dict(group=offset // limit, cases={'include': cases[offset:offset + limit]})
                        for offset in range(0, len(cases), limit)]}


def system_packages(case):
    """Return validated apt package names, rejecting flags and shell expressions.

    Args:
        case (dict): Profile with an optional system_packages list.

    Returns:
        list[str]: Debian package names, optionally qualified by architecture.
    """
    packages = case.get('system_packages', [])
    if not isinstance(packages, list) or any(
            not isinstance(name, str) or not re.fullmatch(r'[a-z0-9][a-z0-9+.-]*(?::[a-z0-9]+)?', name)
            for name in packages):
        raise ValueError('Invalid system package names')
    return packages


def install_system_packages(case):
    """Install declared dependencies, allowing up to ten minutes for downloads.

    Args:
        case (dict): Profile containing optional Debian system package names.
    """
    packages = system_packages(case)
    if not packages:
        return
    # A stalled mirror should retry within the installation budget, rather than
    # consume the whole step waiting for a single download.
    apt = ['sudo', 'apt-get', '-o', 'Acquire::Retries=3',
           '-o', 'Acquire::http::Timeout=30', '-o', 'Acquire::https::Timeout=30']
    command(apt + ['update', '-qq'])
    command(apt + ['install', '-y', '--no-install-recommends', '--', *packages], timeout=600)


def unpack(archive, destination, require_installer=True):
    """Extract regular files under one package directory, rejecting links and escapes.

    Args:
        archive (Path): Downloaded zip or tar archive.
        destination (Path): New extraction directory.
        require_installer (bool): Require a WeeWX installer. False for external projects.

    Returns:
        Path: The single package directory.

    Raises:
        ValueError: The archive has links, unsafe paths or no single package root.
    """
    with (zipfile.ZipFile(archive) if zipfile.is_zipfile(archive)
          else tarfile.open(archive)) as bundle:
        members = bundle.infolist() if isinstance(bundle, zipfile.ZipFile) else bundle.getmembers()
        for member in members:
            name = member.filename if isinstance(member, zipfile.ZipInfo) else member.name
            target = (destination / name).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError('Archive path escapes its directory: ' + name)
            if isinstance(member, zipfile.ZipInfo):
                regular = (member.external_attr >> 16) & 0o170000
                if regular not in (0, 0o100000, 0o040000):
                    raise ValueError('Archive contains a link or special file: ' + name)
            elif not (member.isfile() or member.isdir()):
                raise ValueError('Archive contains a link or special file: ' + name)
        bundle.extractall(destination)
    roots = list(destination.iterdir())
    if len(roots) != 1 or (require_installer and not (roots[0] / 'install.py').is_file()):
        raise ValueError('Archive needs one top-level directory containing install.py')
    return roots[0]


def test_failures(report, allowed_skips):
    """Read failed cases and reject unexpected skips or an entirely skipped suite.

    Args:
        report (Path): pytest JUnit XML file.
        allowed_skips (list[str]): Substrings in explicitly permitted skip reasons.

    Returns:
        list[str]: Failure descriptions, empty for a successful executed suite.
    """
    cases = ET.parse(report).findall('.//testcase')
    failures = []
    executed = 0
    for case in cases:
        name = case.get('classname', '') + '.' + case.get('name', '')
        skipped = case.find('skipped')
        if skipped is not None:
            reason = skipped.get('message', '')
            if not any(allowed in reason for allowed in allowed_skips):
                failures.append(name + ': unexpected skip: ' + reason)
        else:
            executed += 1
            for kind in ('failure', 'error'):
                failure = case.find(kind)
                if failure is not None:
                    failures.append(name + ': ' + failure.get('message', '')[:500])
    if not executed:
        failures.append('No tests executed')
    return failures


def command(args, cwd=None, env=None, input_text=None, timeout=300):
    """Run a test step with its output in the workflow log.

    Args:
        args (list[str]): Command and arguments, without a shell.
        cwd (Path|None): Working directory, or the current directory.
        env (dict|None): Process environment, or the inherited environment.
        input_text (str|None): Explicit fixture answers for an interactive installer.
        timeout (int): Maximum runtime in seconds. Default is 300.
    """
    print('+ ' + ' '.join(args), flush=True)
    subprocess.run(args, cwd=cwd, env=env, input=input_text, text=True, check=True, timeout=timeout)


def run(case, source, work):
    """Install and test the released payload, writing result.json even on failure.

    Args:
        case (dict): One resolved matrix case.
        source (Path): Checkout at the case's source SHA, supplying tests only.
        work (Path): Empty work directory for the archive, station and report.

    Returns:
        int: Zero for success, one for failure or an infrastructure error.
    """
    work = work.resolve()
    work.mkdir(parents=True)
    status, phase = 'error', 'download'
    details = []
    release = case['release']
    try:
        if case.get('pip_packages'):
            phase = 'dependencies'
            # A transitive dependency must not replace the core revision under
            # test. Pip fails on a conflicting WeeWX requirement instead.
            constraints = work / 'constraints.txt'
            constraints.write_text('weewx==' + importlib.metadata.version('weewx') + '\n')
            command([sys.executable, '-m', 'pip', 'install', '--constraint', str(constraints),
                     *case['pip_packages']])
        phase = 'download'
        archive = work / ('package.' + release['archive']['format'])
        with urllib.request.urlopen(release['archive']['url'], timeout=60) as response:
            archive.write_bytes(response.read())
        if hashlib.sha256(archive.read_bytes()).hexdigest() != release['archive']['sha256'].lower():
            raise ValueError('Release archive SHA-256 differs from the catalog')
        external = case.get('kind') in ('external', 'source')
        payload = unpack(archive, work / 'payload', require_installer=not external)
        # Tests come from the release's source revision. Runtime files always
        # come from the published archive, so a broken release cannot be hidden
        # by a newer source file or a file omitted from the download.
        if case.get('kind') != 'skin' and not case.get('tests_path'):
            shutil.copytree(source / 'tests', payload / 'tests', dirs_exist_ok=True)
        status, phase = 'failed', 'requirements'
        import weewx
        if not SpecifierSet(release['requires_python']).contains(platform.python_version()):
            raise ValueError('Python %s is outside %s' %
                             (platform.python_version(), release['requires_python']))
        if case.get('kind') != 'external' and not SpecifierSet(release['requires_weewx']).contains(weewx.__version__, prereleases=True):
            raise ValueError('WeeWX %s is outside %s' %
                             (weewx.__version__, release['requires_weewx']))
        station = work / 'station'
        config = station / 'weewx.conf'
        phase = 'installation'
        if not external:
            command(['weectl', 'station', 'create', str(station), '--no-prompt'])
        if not external and (case.get('kind') == 'skin' or case.get('install_prerequisites') or case.get('initialize_archive')):
            # Skins are installed into an existing WeeWX station. Some installers
            # extend its archive schema, which requires the base database first.
            command([sys.executable, '-c',
                'import sys,weecfg,weewx.manager; '
                '_,c=weecfg.read_config(sys.argv[1]); '
                'weewx.manager.open_manager_with_config(c,"wx_binding",initialize=True).close()', str(config)])
        env = dict(os.environ, PYTHONPATH=str(station / 'bin'))
        if not external:
            status, phase = 'error', 'prerequisites'
            for number, dependency in enumerate(case.get('install_prerequisites', [])):
                checkout = work / ('prerequisite-%s' % number)
                bundle = work / ('prerequisite-%s.zip' % number)
                command(['git', 'clone', '--depth=1', 'https://github.com/' + dependency['repository'] + '.git', str(checkout)])
                command(['git', '-C', str(checkout), 'fetch', '--depth=1', 'origin', dependency['sha']])
                command(['git', '-C', str(checkout), 'archive', '--format=zip', '--prefix=prerequisite/',
                         '--output=' + str(bundle), dependency['sha']])
                command(['weectl', 'extension', 'install', str(bundle), '--config', str(config), '--yes'],
                        input_text='', env=env)
            status, phase = 'failed', 'installation'
            install = ['weectl', 'extension', 'install', str(archive), '--config', str(config), '--yes']
            if case.get('install_input') is not None:
                command(install, input_text=case['install_input'], env=env)
            else:
                command(install, env=env)
            phase = 'installed files'
            command([sys.executable, str(ROOT / 'ci/installed_files.py'),
                     str(payload), str(station)], cwd=payload, env=env)
        # Import in another process so the suite cannot reuse a source module
        # already loaded by this installation check.
        phase = 'imports'
        command([sys.executable, '-c', 'import importlib, sys; '
                 '[importlib.import_module(name) for name in sys.argv[1:]]',
                 *case['imports']], cwd=work, env=env)
        phase = 'tests'
        if case.get('tests_path'):
            tests_path = (ROOT / case['tests_path']).resolve()
            if not tests_path.is_relative_to(ROOT / 'ci/project_tests') or not tests_path.is_dir():
                raise ValueError('Project tests must be an existing directory under ci/project_tests')
            tests = str(tests_path)
            env.update(EXTENSION_PAYLOAD=str(payload), EXTENSION_STATION=str(station),
                       CASE_JSON=json.dumps(case),
                       PYTHONPATH=os.pathsep.join(map(str, (payload / 'bin', station / 'bin', payload))))
        elif case.get('kind') == 'skin':
            tests = str(ROOT / 'ci/skin_tests')
            env.update(SKIN_STATION=str(station), SKIN_PAYLOAD=str(payload), SKIN_CASE=json.dumps(case))
        else:
            tests = 'tests'
            env['PYTHONPATH'] = str(payload / 'bin')
        report = work / 'junit.xml'
        try:
            options = {'timeout': case['test_timeout']} if 'test_timeout' in case else {}
            command([sys.executable, '-m', 'pytest', '-q', '-ra', tests,
                     '--junitxml=' + str(report)], cwd=payload, env=env, **options)
        finally:
            if not report.is_file():
                raise ValueError('No JUnit report was produced')
            details = test_failures(report, case['allowed_skips'])
        if details:
            raise ValueError('Suite contains failures or unexpected skips')
        status = 'passed'
    except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError,
            zipfile.BadZipFile, ET.ParseError) as error:
        details.append(str(error))
        print(str(error), file=sys.stderr)
    result = {'status': status, 'phase': phase, 'details': details}
    (work / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return int(status != 'passed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['matrix', 'shards', 'system', 'run'])
    parser.add_argument('--source', type=Path)
    parser.add_argument('--work', type=Path)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--case-id', type=int)
    parser.add_argument('--weekday', type=int, choices=range(1, 6))
    parser.add_argument('--base', help='test only what changed since this revision')
    args = parser.parse_args()
    if args.action == 'matrix':
        catalog = json.loads((ROOT / 'repository.json').read_text())
        checks = json.loads((ROOT / 'ci/packages.json').read_text())
        external_path = ROOT / 'ci/external.json'
        external = json.loads(external_path.read_text()) if external_path.exists() else {}
        selected = None
        profiles = dict(checks, **{name: item['check_profile'] for name, item in external.items()})
        if args.weekday:
            selected = weekday_selection(profiles, args.weekday)
        elif args.base:
            # Saturday and Sunday fall back to the groups of Monday and Tuesday.
            today = (datetime.date.today().isoweekday() - 1) % 5 + 1
            selected = changed_selection(args.base, catalog, checks, external, today)
        print(json.dumps(matrix(catalog, checks, external, selected)))
    elif args.action == 'shards':
        print(json.dumps(shards(json.loads(args.plan.read_text())), separators=(',', ':')))
    else:
        case = (json.loads(args.plan.read_text())['include'][args.case_id]
                if args.plan else json.loads(os.environ['CASE_JSON']))
        if args.action == 'system':
            install_system_packages(case)
        else:
            sys.exit(run(case, args.source.resolve(), args.work.resolve()))
