# coding: utf-8

import json

from collections import namedtuple, OrderedDict
from datetime import datetime

from django.db.models import Max

from html_source import HtmlSource, RequestError
from html_parser import parse as parse_html

from mosecom_air.api.add import add as add_data
from mosecom_air.api.log import make_one_line
from mosecom_air.api.models import MonitorExcessLog


ExcessWarning = namedtuple('ExcessWarning', ('station', 'substance',
                                             'performed', 'unit', 'value'))


def update(logger):
    data = OrderedDict(get_source_data(logger))
    add_source_data(logger, data)
    monitor_excesses(logger, data)


def get_source_data(logger):
    source = HtmlSource()
    for station_name in source.get_stations_list():
        try:
            html = source.get_station_html(station_name)
            yield station_name, parse_html(html)
            logger.info('action=[get_source_data] result=[success] '
                        'station=[%s]', station_name)
        except RequestError as error:
            logger.error('action=[get_source_data] result=[fail] station=[%s] '
                         '%s', station_name, make_one_line(error))
        except Exception as error:
            logger.error('action=[get_source_data] result=[error] station=[%s] '
                         'reason=[%s]', station_name, make_one_line(error))


def add_source_data(logger, data):
    for station_name, station_data in data.iteritems():
        try:
            add_data(station_name, station_data)
            logger.info('action=[add_source_data] result=[success] '
                        'station=[%s]', station_name)
        except Exception as error:
            logger.error('action=[add_source_data] result=[error] station=[%s] '
                         'reason=[%s]', station_name, make_one_line(error))


def monitor_excesses(logger, data):
    try:
        current = get_current_performed(data)
        if MonitorExcessLog.objects.all().exists():
            latest = (MonitorExcessLog.objects.all()
                      .aggregate(Max('performed'))['performed__max'])
            if latest >= current:
                logger.info('action=[monitor_excesses] result=[nothing to do] '
                            'later_than=[%s]', current)
                return
        else:
            latest = current
        excess_warnings = find_excesses(logger, data, latest)
        MonitorExcessLog(
            performed=current,
            data=json.dumps(list(x._asdict() for x in excess_warnings),
                            default=date_handler, ensure_ascii=False)
        ).save()
        logger.info('action=[monitor_excesses] result=[success] '
                    'later_than=[%s]', latest)
    except Exception as error:
        logger.error('action=[monitor_excesses] result=[error] reason=[%s]',
                     make_one_line(error))


def find_excesses(logger, data, later_than):
    for station_name, station_data in data.iteritems():
        for ew in find_station_excesses(station_name, station_data, later_than):
            log_excess_warning(logger, ew)
            yield ew


def get_current_performed(data):
    return max(x.performed for x in
               (max(y.measurements) for y in data.itervalues()))


def find_station_excesses(station_name, data, later_than):
    for measurement in data.measurements:
        if measurement.performed > later_than and is_excess(measurement):
            yield make_excess_warning(station_name, measurement)


def is_excess(measurement):
    return (unicode(measurement.unit) == u'единицы ПДК м.р.'
            and measurement.value is not None
            and measurement.value >= 1.0)


def make_excess_warning(station_name, measurement):
    return ExcessWarning(
        station=station_name,
        substance=measurement.substance,
        performed=measurement.performed,
        unit=measurement.unit,
        value=measurement.value,
    )


def log_excess_warning(logger, excess_warning):
    logger.warning('reason=[excess detected] station=[%s] substance=[%s] '
                   'performed=[%s] unit=[%s] value=[%s]', *excess_warning)


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def date_handler(obj):
    return obj.strftime(DATETIME_FORMAT) if isinstance(obj, datetime) else obj
