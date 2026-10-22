"""Parse ACIS missing, trace and extreme records without HTTP."""

from user.climate.acis import acis_struct, gen_acis_records


def test_acis_values_dates_and_reductions():
    data = {'meta': {'name': 'Fixture', 'state': 'OR'}, 'smry': [
        [['38.5', '2000-01-02'], ['M', '2000-01-03']],
        [['58', '1997-01-02']], [], [], [], [],
        [['T', '2000-01-02']], [], []]}
    rows = list(gen_acis_records(data, 'USC00354003'))
    assert rows == [
        ('USC00354003', 1, 2, 1, 'outTemp', 'high', 'avg', 38.5, None),
        ('USC00354003', 1, 3, 1, 'outTemp', 'high', 'avg', None, None),
        ('USC00354003', 1, 2, 1, 'outTemp', 'high', 'max', 58.0, 1997),
        ('USC00354003', 1, 2, 1, 'precip', 'sum', 'max', 0.0, 2000)]
    query = acis_struct('USC00354003')
    assert query['sid'] == 'USC00354003'
    assert len(query['elems']) == 9
    assert query['elems'][6]['name'] == 'pcpn'
