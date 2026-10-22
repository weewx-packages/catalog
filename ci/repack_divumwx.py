#!/usr/bin/env python3
"""Repackage the audited DivumWX 1.7.0 source ZIP as 1.7.0.post1.

Usage: python ci/repack_divumwx.py SOURCE.zip OUTPUT.zip
The adjacent source manifest pins every input file to the audited tag.
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

VERSION = '1.7.0.post1'
FREE_FONTS = {'weathericons-regular-webfont.' + suffix
              for suffix in ['eot', 'svg', 'ttf', 'woff', 'woff2']} | {'weathertext.woff2'}
SUPPLEMENTS = {'WEATHER-ICONS-NOTICE.txt': 'e41b2eeb8c9a80fbea6fb248fcc3bbaa29f60a55250f55235e12ce503c9a04a7', 'INTERFACE-NOTICE.txt': '4ee714d6a2318b2ee2968ba9b144d8275ad57e79ebf1626949a6bf93260ef2f4'}
FONT_DIR = 'divumwx/css/fonts/'
SYSTEM_FONT = 'system-ui, "Segoe UI Symbol", "Apple Symbols", sans-serif'
ZODIAC = '\u2648\u2649\u264a\u264b\u264c\u264d\u264e\u264f\u2650\u2651\u2652\u2653'
NOTICE = '''DivumWX package changes, 2026-10-22
Source: https://github.com/weewx-packages/weewx-divumwx
Revision: ac720ea8b52158fe099327264f02368c0a3044d0
Package version: 1.7.0.post1

This package omits all original font-directory assets except IBM Plex Sans
and its original OFL.txt, the official Weather Icons fonts and the OFL-licensed
Interface weathertext.woff2. Supplemental notices contain their full OFL text. The personal-use Dirtylane demo and its nested ZIP
are omitted because general redistribution permission has not been established.
Other omitted fonts have absent, incomplete, or scope-restricted permissions
in this source tree. These observations do not imply that all personal-use or
noncommercial fonts are prohibited from redistribution.

AstroDotBasic letter glyphs are replaced with standard Unicode zodiac characters
and a system font stack. Glyph appearance and font metrics depend on the browser.
Original copyright and license files are retained unchanged. IBM Plex Sans is
licensed under the included SIL Open Font License 1.1, with reserved name Plex.
The original GPL texts remain in LICENSE and license.txt. This notice records
packaging changes and grants no rights to excluded assets.
'''


def digest(data):
    """Return the SHA-256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def read_source(source, manifest):
    """Read a pinned source ZIP without extracting it.

    Args:
        source (str|Path): Source archive with one top-level directory.
        manifest (dict): Relative paths and SHA-256 digests of all source files.

    Returns:
        dict: Relative paths and file bytes.

    Raises:
        ValueError: The archive has unsafe paths or differs from the audited input.
    """
    files = {}
    roots = set()
    names = set()
    with zipfile.ZipFile(source) as archive:
        total = 0
        for member in archive.infolist():
            parts = PurePosixPath(member.filename).parts
            if (member.filename.startswith('/') or '\\' in member.filename
                    or '..' in parts or len(parts) < 1
                    or member.filename in names
                    or stat.S_ISLNK(member.external_attr >> 16)):
                raise ValueError('Unsafe or duplicate ZIP member: %s' % member.filename)
            names.add(member.filename)
            roots.add(parts[0])
            if member.is_dir():
                continue
            if len(parts) < 2:
                raise ValueError('Expected a top-level source directory')
            total += member.file_size
            if total > 64 * 1024 * 1024:
                raise ValueError('Source archive exceeds audited size limit')
            relative = '/'.join(parts[1:])
            if relative in files:
                raise ValueError('Duplicate normalized file: %s' % relative)
            files[relative] = archive.read(member)
    if len(roots) != 1 or {p: digest(b) for p, b in files.items()} != manifest:
        raise ValueError('Source differs from the complete audited tag manifest')
    return files


def repackage(source, destination, manifest_path=None):
    """Write a new archive; refuse an existing destination or changed input.

    Args:
        source (str|Path): Source ZIP containing the audited tag.
        destination (str|Path): New ZIP filename.
        manifest_path (str|Path|None): Pinned manifest, or the adjacent audit manifest.

    Returns:
        dict: Removed paths, changed paths, retained license hashes and output hash.
    """
    if manifest_path is None:
        manifest_path = Path(__file__).parent / 'divumwx-remediation/source-manifest.json'
    manifest = json.loads(Path(manifest_path).read_text())
    files = read_source(source, manifest)
    removed = []
    for path in list(files):
        if path.startswith(FONT_DIR):
            name = path[len(FONT_DIR):]
            if name != 'OFL.txt' and name not in FREE_FONTS and not re.fullmatch(r'IBMPlexSans-[A-Za-z]+\.ttf', name):
                removed.append(path)
                del files[path]
    for name, expected_hash in SUPPLEMENTS.items():
        data = (Path(__file__).parent / 'divumwx-remediation/license-supplements' / name).read_bytes()
        if digest(data) != expected_hash:
            raise ValueError('License supplement differs from audited source: %s' % name)
        files[FONT_DIR + name] = data
    changed = []
    astro = 'divumwx/modalAstroclock.html'
    text = files[astro].decode()
    text, count = re.subn(r"@font-face\s*\{\s*font-family: 'AstroDotBasic';\s*src: url\('css/fonts/AstroDotBasic.ttf'\) format\('truetype'\);\s*\}",
                          '/* Modified 2026-10-22: use standard Unicode zodiac symbols. */', text)
    if count != 1 or text.count("'AstroDotBasic'") != 2:
        raise ValueError('Unexpected AstroDot font declarations')
    text = text.replace("'AstroDotBasic'", repr(SYSTEM_FONT))
    text = text.replace("'abcdefghijkl'.split('')", repr(ZODIAC) + ".split('')")
    for letter, symbol in zip('abcdefghijkl', ZODIAC):
        text = text.replace("char: '%s'" % letter, "char: '%s'" % symbol)
    files[astro] = text.encode()
    changed.append(astro)
    for path, old_version in [('bin/user/divumwx_version.py', '1.7.0'),
                              ('divumwx_version.py', '1.3.1')]:
        text = files[path].decode()
        text, count = re.subn(r'DIVUMWX_VERSION = "%s"' % re.escape(old_version),
                              '# Modified 2026-10-22: separately version the sanitized package.\n'
                              'DIVUMWX_VERSION = "%s"' % VERSION, text)
        if count != 1:
            raise ValueError('Unexpected release version in %s' % path)
        files[path] = text.encode()
        changed.append(path)
    installer = files['install.py'].decode()
    old = 'DIVUMWX_VERSION = _load_divumwx_version()'
    if installer.count(old) != 1:
        raise ValueError('Unexpected installer version assignment')
    files['install.py'] = installer.replace(old,
        '# Modified 2026-10-22: sanitized package has a distinct version.\n'
        'DIVUMWX_VERSION = "%s"' % VERSION).encode()
    changed.append('install.py')
    files['PACKAGING-NOTICE.txt'] = NOTICE.encode()
    prefix = 'weewx-divumwx-%s/' % VERSION
    # Exclusive creation protects both published bytes and local source archives.
    with open(destination, 'xb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for path, data in sorted(files.items()):
                info = zipfile.ZipInfo(prefix + path, (2026, 10, 22, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                archive.writestr(info, data)
    licenses = {p: digest(b) for p, b in files.items()
                if re.search(r'(^|/)(license[^/]*|notice[^/]*|ofl\.txt|copying[^/]*|[^/]*-NOTICE\.txt)$', p, re.I)}
    return {'version': VERSION, 'excluded_paths': sorted(removed),
            'changed_paths': changed, 'retained_licenses': licenses,
            'output_sha256': digest(Path(destination).read_bytes())}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(json.dumps(repackage(args.source, args.destination), indent=2))
