"""Check conditional HTTP downloads and UTC header dates."""

from types import SimpleNamespace
import requests
from user import weatherservicesutil as util


def test_http_timestamp_and_conditional_content():
    stamp = 1721218394.5
    header = 'Wed, 17 Jul 2024 12:13:14 GMT'
    assert util.http_timestamp_to_ts(header) == stamp
    assert util.ts_to_http_timestamp(stamp) == header
    calls = []
    def get(url, **kwargs):
        calls.append(kwargs)
        return SimpleNamespace(url=url, status_code=200, content=b'station;TT\n1048;0\n',
                               headers={'Etag': 'fixture', 'Last-Modified': header})
    assert util.wget_extended('https://fixture.invalid/data', session=SimpleNamespace(get=get),
                              if_modified_since=stamp) == ('fixture', stamp, b'station;TT\n1048;0\n', 200)
    assert calls[0]['headers']['If-Modified-Since'] == header
    assert calls[0]['timeout'] == 5
    assert util.http_timestamp_to_ts('broken') is None


def test_not_modified_and_timeout():
    response = SimpleNamespace(url='https://fixture.invalid/data', status_code=304,
                               headers={'Etag': 'same'})
    assert util.wget_extended(response.url, session=SimpleNamespace(get=lambda *a, **k: response),
                              if_modified_since=0) == ('same', None, None, 304)
    def timeout(*args, **kwargs):
        raise requests.exceptions.Timeout()
    assert util.wget_extended(response.url, session=SimpleNamespace(get=timeout)) == (None, None, None, None)


def test_cli_links_are_station_local(station):
    commands = station / 'bin/commands'
    for name in ('dwd-cap-warnings', 'bbk-warnings', 'msc-warnings'):
        link = commands / name
        assert link.is_symlink()
        assert link.resolve() == station / 'bin/user/capwarnings.py'
