"""Check real Git ref updates and refusal to overwrite divergent mirror history."""

from pathlib import Path
import subprocess

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'sync-weewx.sh'


def git(directory, *args):
    """Run Git in a disposable test repository and return its output.

    Args:
        directory (Path): Working repository.
        *args (str): Git subcommand and arguments.

    Returns:
        str: Standard output without surrounding whitespace.
    """
    return subprocess.run(['git', '-C', str(directory), *args], check=True,
                          text=True, capture_output=True).stdout.strip()


@pytest.fixture
def repositories(tmp_path):
    """Create upstream branches, an annotated release tag and an empty mirror.

    Args:
        tmp_path (Path): Temporary parent directory.

    Returns:
        tuple[Path, Path]: Upstream working tree and bare mirror.
    """
    upstream, mirror = tmp_path / 'upstream', tmp_path / 'mirror.git'
    subprocess.run(['git', 'init', '-b', 'master', str(upstream)], check=True, capture_output=True)
    subprocess.run(['git', 'init', '--bare', str(mirror)], check=True, capture_output=True)
    git(upstream, 'config', 'user.name', 'Mirror test')
    git(upstream, 'config', 'user.email', 'test@example.test')
    (upstream / 'version').write_text('first\n')
    git(upstream, 'add', 'version')
    git(upstream, 'commit', '-m', 'First version')
    git(upstream, 'branch', 'development')
    git(upstream, 'tag', '-a', 'v1', '-m', 'First release')
    return upstream, mirror


def sync(upstream, mirror):
    """Run the production sync command with local repository URLs.

    Args:
        upstream (Path): Upstream working tree with branches and tags.
        mirror (Path): Bare destination repository.

    Returns:
        subprocess.CompletedProcess[str]: Result including Git's exit status and output.
    """
    return subprocess.run(['bash', str(SCRIPT), str(upstream), str(mirror)],
                          text=True, capture_output=True)


def test_sync_copies_all_refs_and_history_and_can_repeat(repositories):
    upstream, mirror = repositories
    assert sync(upstream, mirror).returncode == 0
    assert git(mirror, 'show-ref') == git(upstream, 'show-ref')
    first = git(upstream, 'rev-parse', 'master')
    (upstream / 'version').write_text('second\n')
    git(upstream, 'commit', '-am', 'Second version')
    git(upstream, 'branch', 'feature')
    git(upstream, 'tag', 'v2')
    assert sync(upstream, mirror).returncode == 0
    assert git(mirror, 'show-ref') == git(upstream, 'show-ref')
    assert git(mirror, 'show', first + ':version') == 'first'
    assert sync(upstream, mirror).returncode == 0


def test_divergence_prevents_partial_update(repositories):
    upstream, mirror = repositories
    assert sync(upstream, mirror).returncode == 0
    (upstream / 'version').write_text('second\n')
    git(upstream, 'commit', '-am', 'Second version')
    divergent = git(upstream, 'rev-parse', 'master')
    # Put an upstream commit in the mirror, then rewrite upstream to a sibling.
    assert sync(upstream, mirror).returncode == 0
    git(upstream, 'reset', '--hard', 'HEAD~1')
    (upstream / 'version').write_text('alternative\n')
    git(upstream, 'commit', '-am', 'Alternative history')
    git(upstream, 'branch', '-f', 'development', 'master')
    before = git(mirror, 'show-ref')
    result = sync(upstream, mirror)
    assert result.returncode != 0
    assert 'rejected' in result.stderr
    assert git(mirror, 'show-ref') == before
    assert git(mirror, 'rev-parse', 'master') == divergent


def test_upstream_deletion_keeps_the_mirrored_branch(repositories):
    upstream, mirror = repositories
    assert sync(upstream, mirror).returncode == 0
    development = git(mirror, 'rev-parse', 'development')
    git(upstream, 'branch', '-D', 'development')
    assert sync(upstream, mirror).returncode == 0
    assert git(mirror, 'rev-parse', 'development') == development
