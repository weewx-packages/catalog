"""Set and restore the real process title in the isolated test process."""

from types import SimpleNamespace
import setproctitle
from user.SetProcessName import SetProcessName


def test_real_process_title():
    previous = setproctitle.getproctitle()
    try:
        SetProcessName(SimpleNamespace(), {'SetProcessName': {'name': 'weewx-ci-fixture'}})
        assert setproctitle.getproctitle() == 'weewx-ci-fixture'
    finally:
        setproctitle.setproctitle(previous)
