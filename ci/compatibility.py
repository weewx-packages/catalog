"""Test catalog release archives with tests from their pinned source revisions.

The workflow installs WeeWX and pytest before calling ``run``. Downloads and
checksum failures are infrastructure errors; installation, import and test
failures are compatibility failures. Only the latter produce package issues.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

from packaging.specifiers import SpecifierSet
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]
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


def matrix(catalog, checks):
    """Resolve one immutable test case per package, WeeWX branch and Python.

    Args:
        catalog (dict): The published package catalog.
        checks (dict): Test source, imports and permitted skips by package ID.

    Returns:
        dict: GitHub Actions matrix with an ``include`` list.

    Raises:
        ValueError: A package has no check, or a check has no package.
    """
    package_ids = [p['id'] for p in catalog['packages']]
    if len(set(package_ids)) != len(package_ids) or set(package_ids) != set(checks):
        raise ValueError('Every catalog package needs exactly one entry in ci/packages.json')
    upstream = {branch: revision('weewx/weewx', branch)
                for branch in BRANCHES}
    cases = []
    for package in catalog['packages']:
        release = latest_release(package)
        check = checks[package['id']]
        ref = check['ref'].format(version=release['version'])
        source_sha = revision(check['repository'], ref)
        for branch, weewx_sha in upstream.items():
            for python in PYTHONS:
                cases.append(dict(package=package['id'], installer_name=package['installer_name'],
                                  release=release, **check, source_sha=source_sha,
                                  branch=branch, weewx_sha=weewx_sha, python=python))
    return {'include': cases}


def unpack(archive, destination):
    """Extract regular files under one package directory, rejecting links and escapes.

    Args:
        archive (Path): Downloaded zip or tar archive.
        destination (Path): New extraction directory.

    Returns:
        Path: The package directory containing install.py.

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
    if len(roots) != 1 or not (roots[0] / 'install.py').is_file():
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


def command(args, cwd=None, env=None):
    """Run a test step with its output in the workflow log.

    Args:
        args (list[str]): Command and arguments, without a shell.
        cwd (Path|None): Working directory, or the current directory.
        env (dict|None): Process environment, or the inherited environment.
    """
    print('+ ' + ' '.join(args), flush=True)
    subprocess.run(args, cwd=cwd, env=env, check=True, timeout=300)


def run(case, source, work):
    """Install and test the released payload, writing result.json even on failure.

    Args:
        case (dict): One resolved matrix case.
        source (Path): Checkout at the case's source SHA, supplying tests only.
        work (Path): Empty work directory for the archive, station and report.

    Returns:
        int: Zero for success, one for failure or an infrastructure error.
    """
    work.mkdir(parents=True)
    status, phase = 'error', 'download'
    details = []
    release = case['release']
    try:
        archive = work / ('package.' + release['archive']['format'])
        with urllib.request.urlopen(release['archive']['url'], timeout=60) as response:
            archive.write_bytes(response.read())
        if hashlib.sha256(archive.read_bytes()).hexdigest() != release['archive']['sha256'].lower():
            raise ValueError('Release archive SHA-256 differs from the catalog')
        payload = unpack(archive, work / 'payload')
        # Tests come from the release's source revision. Runtime files always
        # come from the published archive, so a broken release cannot be hidden
        # by a newer source file or a file omitted from the download.
        shutil.copytree(source / 'tests', payload / 'tests', dirs_exist_ok=True)
        status, phase = 'failed', 'requirements'
        import weewx
        if not SpecifierSet(release['requires_python']).contains(platform.python_version()):
            raise ValueError('Python %s is outside %s' %
                             (platform.python_version(), release['requires_python']))
        if not SpecifierSet(release['requires_weewx']).contains(weewx.__version__, prereleases=True):
            raise ValueError('WeeWX %s is outside %s' %
                             (weewx.__version__, release['requires_weewx']))
        station = work / 'station'
        config = station / 'weewx.conf'
        phase = 'installation'
        command(['weectl', 'station', 'create', str(station), '--no-prompt'])
        command(['weectl', 'extension', 'install', str(archive), '--config', str(config), '--yes'])
        env = dict(os.environ, PYTHONPATH=str(station / 'bin'))
        # Import in another process so the suite cannot reuse a source module
        # already loaded by this installation check.
        phase = 'imports'
        command([sys.executable, '-c', 'import importlib, sys; '
                 '[importlib.import_module(name) for name in sys.argv[1:]]',
                 *case['imports']], cwd=work, env=env)
        phase = 'tests'
        env['PYTHONPATH'] = str(payload / 'bin')
        report = work / 'junit.xml'
        try:
            command([sys.executable, '-m', 'pytest', '-q', '-ra', 'tests',
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
    parser.add_argument('action', choices=['matrix', 'run'])
    parser.add_argument('--source', type=Path)
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    if args.action == 'matrix':
        catalog = json.loads((ROOT / 'repository.json').read_text())
        checks = json.loads((ROOT / 'ci/packages.json').read_text())
        print(json.dumps(matrix(catalog, checks)))
    else:
        sys.exit(run(json.loads(os.environ['CASE_JSON']), args.source.resolve(), args.work.resolve()))
