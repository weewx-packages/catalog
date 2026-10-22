"""Require a declared release, external or component check for every tracked source."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def coverage(mirrors, packages, external):
    """Match tracked sources to their checks without hiding component-only coverage.

    Args:
        mirrors (list[dict]): Tracked repositories and weekly assignments.
        packages (dict): Catalog check profiles indexed by package ID.
        external (dict): Non-catalog releases with their check_profile.

    Returns:
        list[dict]: Repository, weekday and each declared check's coverage.

    Raises:
        ValueError: A tracked repository has no check or a check has no tracked source.
    """
    rows = {item['fork']: dict(repository=item['fork'], weekday=item['weekday'], checks=[])
            for item in mirrors}
    profiles = [(name, profile, 'release') for name, profile in packages.items()]
    profiles.extend((name, item['check_profile'], 'external') for name, item in external.items())
    for name, profile, default in profiles:
        repository = profile['repository']
        if repository not in rows:
            raise ValueError('Check has no tracked source: ' + repository)
        rows[repository]['checks'].append(dict(id=name, coverage=profile.get('coverage', default),
                                              tests_path=profile.get('tests_path', 'source/tests')))
    missing = sorted(name for name, row in rows.items() if not row['checks'])
    if missing:
        raise ValueError('Tracked sources without checks: ' + ', '.join(missing))
    return [rows[name] for name in sorted(rows)]


if __name__ == '__main__':
    print(json.dumps(coverage(json.loads((ROOT / 'ci/mirrors.json').read_text()),
                              json.loads((ROOT / 'ci/packages.json').read_text()),
                              json.loads((ROOT / 'ci/external.json').read_text())), indent=2))
