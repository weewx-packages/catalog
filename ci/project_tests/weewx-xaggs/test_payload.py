"""Run threshold aggregations against actual SQLite daily summaries."""

import sqlite3
from types import SimpleNamespace
import pytest
import weewx
import weewx.units
from weeutil.weeutil import TimeSpan
from user.xaggs import XAggsAvg


def test_threshold_boundaries_and_temperature_units():
    with sqlite3.connect(':memory:') as connection:
        connection.execute('CREATE TABLE archive_day_outTemp(dateTime INTEGER, wsum REAL, sumtime REAL)')
        connection.executemany('INSERT INTO archive_day_outTemp VALUES(?,?,?)',
                               [(0, 0, 300), (86400, 3000, 300), (172800, 6000, 300)])
        manager = SimpleNamespace(std_unit_system=weewx.METRIC, table_name='archive',
                                  getSql=lambda sql: connection.execute(sql).fetchone())
        xtype = XAggsAvg()
        val = weewx.units.ValueTuple(50, 'degree_F', 'group_temperature')
        for agg, expected in [('avg_ge', 2), ('avg_gt', 1), ('avg_le', 2), ('avg_lt', 1)]:
            assert xtype.get_aggregate('outTemp', TimeSpan(0, 259200), agg, manager, val=val) == (expected, 'count', 'group_count')
        with pytest.raises(weewx.UnknownAggregation):
            xtype.get_aggregate('outTemp', TimeSpan(0, 259200), 'bad', manager, val=val)
