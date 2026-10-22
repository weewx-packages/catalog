"""Test catalog release archives with tests from their pinned source revisions.

The workflow installs WeeWX and pytest before calling ``run``. Downloads and
checksum failures are infrastructure errors; installation, import and test
failures are compatibility failures. Only the latter produce package issues.
"""

import argparse
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


def latest_release(package):
    """Select the newest non-yanked stable release, independent of array order.

    Args:
        package (dict): A catalog package with its releases.

    Returns:
        dict: The selected release.
    """
    return max((r for r in package['releases']
                if not r.get('yanked') and not Version(r['version']).is_prerelease),
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
        external (dict|None): Non-extension projects with a release and check_profile.
        selected (set[str]|None): Package IDs to run, or None for all projects.

    Returns:
        dict: GitHub Actions matrix with an ``include`` list.

    Raises:
        ValueError: A package has no check, or a check has no package.
    """
    package_ids = [p['id'] for p in catalog['packages']]
    if len(set(package_ids)) != len(package_ids) or set(package_ids) != set(checks):
        raise ValueError('Every catalog package needs exactly one entry in ci/packages.json')
    external = external or {}
    if set(external) & set(checks):
        raise ValueError('External project IDs must not collide with catalog packages')
    packages = catalog['packages'] + [dict(id=name, installer_name=name, releases=[item['release']])
                                      for name, item in external.items()]
    checks = dict(checks, **{name: dict(item['check_profile'], kind='external')
                            for name, item in external.items()})
    upstream = {branch: revision(WEEWX_REPOSITORY, branch)
                for branch in BRANCHES}
    cases = []
    for package in packages:
        if selected is not None and package['id'] not in selected:
            continue
        release = latest_release(package)
        check = checks[package['id']]
        system_packages(check)
        for dependency in check.get('pip_packages', []):
            if canonicalize_name(Requirement(dependency).name) == 'weewx':
                raise ValueError('Package dependencies must not replace the WeeWX checkout')
        ref = check['ref'].format(version=release['version'])
        source_sha = revision(check['repository'], ref)
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


def command(args, cwd=None, env=None, input_text=None):
    """Run a test step with its output in the workflow log.

    Args:
        args (list[str]): Command and arguments, without a shell.
        cwd (Path|None): Working directory, or the current directory.
        env (dict|None): Process environment, or the inherited environment.
        input_text (str|None): Explicit fixture answers for an interactive installer.
    """
    print('+ ' + ' '.join(args), flush=True)
    subprocess.run(args, cwd=cwd, env=env, input=input_text, text=True, check=True, timeout=300)


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
        external = case.get('kind') == 'external'
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
        if not external and not SpecifierSet(release['requires_weewx']).contains(weewx.__version__, prereleases=True):
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
            command([sys.executable, '-m', 'pytest', '-q', '-ra', tests,
                     '--junitxml=' + str(report)], cwd=payload, env=env)
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
    args = parser.parse_args()
    if args.action == 'matrix':
        catalog = json.loads((ROOT / 'repository.json').read_text())
        checks = json.loads((ROOT / 'ci/packages.json').read_text())
        external_path = ROOT / 'ci/external.json'
        external = json.loads(external_path.read_text()) if external_path.exists() else {}
        selected = None
        if args.weekday:
            mirrors = json.loads((ROOT / 'ci/mirrors.json').read_text())
            repositories = {item['fork'] for item in mirrors
                            if item['weekday'] == args.weekday}
            profiles = dict(checks, **{name: item['check_profile'] for name, item in external.items()})
            selected = {name for name, profile in profiles.items() if profile['repository'] in repositories}
        print(json.dumps(matrix(catalog, checks, external, selected)))
    elif args.action == 'shards':
        print(json.dumps(shards(json.loads(args.plan.read_text())), separators=(',', ':')))
    else:
        case = (json.loads(args.plan.read_text())['include'][args.case_id]
                if args.plan else json.loads(os.environ['CASE_JSON']))
        if args.action == 'system':
            packages = system_packages(case)
            if packages:
                command(['sudo', 'apt-get', 'update', '-qq'])
                command(['sudo', 'apt-get', 'install', '-y', '--', *packages])
        else:
            sys.exit(run(case, args.source.resolve(), args.work.resolve()))
