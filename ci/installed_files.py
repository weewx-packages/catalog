"""Check that an installer leaves the released Python runtime in the station."""

from pathlib import Path
import sys


def changed_files(paths):
    """Find missing or changed Python files from WeeWX's actual destination mapping.

    Args:
        paths (Iterable[tuple[str, str]]): Source and installed paths from the core installer.

    Returns:
        list[str]: Installed runtime paths that differ from the released source.
    """
    changed = []
    for source_name, destination_name in paths:
        source, destination = Path(source_name), Path(destination_name)
        if source.suffix == '.py' and (not destination.is_file()
                                      or destination.read_bytes() != source.read_bytes()):
            changed.append(str(destination))
    return changed


def unsupported_paths(paths, station):
    """Find destinations outside the repository client's managed user and skin roots.

    Args:
        paths (Iterable[tuple[str, str]]): Source and destination paths from the core.
        station (Path): Disposable station with its default user and skin directories.

    Returns:
        list[str]: Destinations that the repository client cannot manage.
    """
    roots = [(station / name).resolve() for name in ('bin/user', 'skins')]
    return [destination for _, destination in paths
            if not any(Path(destination).resolve().is_relative_to(root) for root in roots)]


if __name__ == '__main__':
    import weecfg
    import weecfg.extension

    # Old installers use WeeWX's historical setup alias. Match the CLI loader
    # without rerunning configure(), which may prompt or change station files.
    sys.modules['setup'] = weecfg.extension
    payload, station = map(Path, sys.argv[1:])
    _, installer = weecfg.get_extension_installer(str(payload))
    paths = list(weecfg.extension.ExtensionEngine._gen_file_paths(
        str(station), str(payload), installer.get('files', [])))
    unsupported = unsupported_paths(paths, station)
    if unsupported:
        raise ValueError('Destinations outside repository-managed roots: ' + ', '.join(unsupported))
    changed = changed_files(paths)
    if changed:
        raise ValueError('Installed Python differs from release: ' + ', '.join(changed))
