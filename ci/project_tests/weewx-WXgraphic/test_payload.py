"""Render the installed WXgraphic skin against a local SQLite archive."""

import importlib.util
import logging
from pathlib import Path
import sys
from types import SimpleNamespace

import configobj
import weecfg
import weewx
import weewx.manager
import weewx.reportengine
import weewx.station


def test_station_skin_report_and_searchlist(payload, station, caplog, tmp_path):
    path = payload / 'bin/user/wxgraphic.py'
    spec = importlib.util.spec_from_file_location('user.wxgraphic', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    skin = configobj.ConfigObj(str(payload / 'skins/WXgraphic/skin.conf'))
    _, config = weecfg.read_config(str(station / 'weewx.conf'))
    skin.setdefault('Units', {}).setdefault('Ordinates', {})['directions'] = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N/A']
    searchlist = module.WXgraphic(SimpleNamespace(config_dict=config, skin_dict=skin))
    assert searchlist.title_here == config['Station']['location']
    assert searchlist.img_type == 'png'
    assert searchlist.d_f_p.endswith('/DATA/wxgraphic_weewx.txt')
    end = 1704110400
    config['DatabaseTypes']['SQLite']['SQLITE_ROOT'] = str(tmp_path / 'archive')
    with weewx.manager.open_manager_with_config(config, 'wx_binding', initialize=True) as manager:
        manager.addRecord([dict(dateTime=stamp, usUnits=weewx.METRICWX, interval=5,
            outTemp=0, inTemp=20, outHumidity=50, inHumidity=40,
            barometer=1013.25, windSpeed=0, windDir=0, rain=0, rainRate=0,
            dewpoint=-5, windchill=0, heatindex=0) for stamp in range(end-3600, end+1, 300)])
        manager.backfill_day_summary()
    output = tmp_path / 'generated'
    config['StdReport']['WXgraphic']['HTML_ROOT'] = str(output)
    caplog.set_level(logging.ERROR)
    weewx.reportengine.StdReportEngine(config, weewx.station.StationInfo(**config['Station']),
                                       gen_ts=end).run(reports=['WXgraphic'])
    errors = [r.getMessage() for r in caplog.records if r.levelno >= logging.ERROR]
    assert not errors, '\n'.join(errors)
    config_file = output / 'config.txt'
    assert config_file.is_file()
    assert 'banner_big' in config_file.read_text()
    data = (output / 'DATA/wxgraphic_weewx.txt').read_text()
    fields = data.strip().split(';')
    assert fields[1] == '01/01/24'
    assert fields[2] == '32.0'
    assert fields[9:11] == ['0.0', 'N']
