"""Exercise installed dashboard services, search lists and report generation."""
import inspect
import json
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest
import weecfg
import weewx
import weewx.manager
import weewx.reportengine
import weewx.station
from weeutil.weeutil import get_object


def test_installed_services_and_dashboard(station, caplog):
    _, config = weecfg.read_config(str(station / 'weewx.conf'))
    end = 1751457600
    report = config['StdReport']['EcowittConsoleEmulatorReport']
    output = station / 'dashboard'
    report['HTML_ROOT'] = str(output)
    report['enable'] = True
    config['StdReport']['Defaults']['unit_system'] = 'METRICWX'
    record = dict(dateTime=end, usUnits=weewx.METRICWX, interval=5,
                  outTemp=20, inTemp=22, outHumidity=60, inHumidity=50,
                  barometer=1015, pressure=1000, altimeter=1015,
                  windSpeed=2, windDir=180, windGust=4, windGustDir=180,
                  rain=0, rainRate=0, radiation=300, UV=2, dewpoint=10,
                  windchill=20, heatindex=20, ET=0)
    caplog.set_level(logging.ERROR)
    bindings = []
    info = weewx.station.StationInfo(**config['Station'])
    with weewx.manager.DBBinder(config) as binder:
        source = binder.get_manager('wx_binding', initialize=True)
        source.addRecord([dict(record, dateTime=stamp) for stamp in
                          range(end - 86400 + 300, end + 1, 300)], update=True)
        source.backfill_day_summary()
        engine = SimpleNamespace(db_binder=binder, stn_info=info,
                                 bind=lambda *args: bindings.append(args))
        config['EcowittConsoleEmulator']['backfill_days'] = 'all'
        archive_class = get_object('user.ecowitt_console_emulator.EcowittConsoleEmulatorArchive')
        assert Path(inspect.getfile(archive_class)).is_relative_to(station / 'bin')
        # Exercise creation and history copying on every invocation, including
        # repeated runs against a station that already rendered a dashboard.
        database_name = config['DataBindings']['ecce_binding']['database']
        database = weewx.manager.get_database_dict_from_config(config, database_name)
        archive_file = Path(database['SQLITE_ROOT']) / database['database_name']
        assert archive_file.is_relative_to(station)
        archive_file.unlink(missing_ok=True)
        archive = archive_class(engine, config)
        assert archive.dbm is not None
        assert archive.dbm.getRecord(end)['outTemp'] == 20
        archive.new_archive_record(SimpleNamespace(record=dict(record, dateTime=end+300,
                                                               outTemp=25)))
        assert archive.dbm.getRecord(end+300)['outTemp'] == 25
        # Use the skin's report binding, so Cheetah must load its installed SearchList.
        assert get_object('user.ecowitt_console_emulator.EcowittConsoleEmulatorData')
        config['EcowittConsoleEmulator']['enable'] = True
        config['EcowittConsoleEmulator']['interval'] = 0
        live = get_object('user.ecowitt_console_emulator.EcowittConsoleEmulatorLive')(engine, config)
        live.new_loop_packet(SimpleNamespace(packet=dict(record, usUnits=weewx.US,
                                                          outTemp=32, windSpeed=2.23694)))
        packet = json.loads((output / 'live.json').read_text())
        assert packet['data']['outTemp'] == 0
        assert packet['data']['windSpeed'] == pytest.approx(1, abs=0.001)
        assert weewx.NEW_ARCHIVE_RECORD in {item[0] for item in bindings}
        report_engine = weewx.reportengine.StdReportEngine(config, info, gen_ts=end,
                                                          first_run=True)
        report_engine.run(reports=['EcowittConsoleEmulatorReport'])
    errors = [entry.getMessage() for entry in caplog.records if entry.levelno >= logging.ERROR]
    assert not errors, '\n'.join(errors)
    for name in ['index.html', 'ecowitt.json', 'chart_day.json']:
        file = output / name
        assert file.is_file() and file.stat().st_size > 20, str(file)
        if file.suffix == '.json':
            assert json.loads(file.read_text())
    assert '<html' in (output / 'index.html').read_text().lower()

    dashboard = json.loads((output / 'ecowitt.json').read_text())['data']
    assert dashboard['archiveTime'] == end
    assert dashboard['out']['temp'] == 20
    assert dashboard['out']['hi'] == 25
    assert dashboard['wind']['speed'] == 2
