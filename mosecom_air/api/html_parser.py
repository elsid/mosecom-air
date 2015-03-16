# coding: utf-8

import re

from datetime import datetime
from pyquery import PyQuery

from mosecom_air.api.parser import Substance, Measurement, Result

SUBSTANCE_RE = re.compile(r'^(?P<name>[^\s_]*)(?:\s*\((?P<alias>.*?)\))?')
STATION_ALIAS_RE = re.compile(ur'«(?P<alias>[^»]*)»')
FULL_DATETIME_FORMAT = '%d.%m.%Y %H:%M'
SHORT_DATETIME_FORMAT = '%H:%M'


def get_table_html(html):
    return PyQuery(html)('table').outerHtml()


class ParseSubstanceHeaderError(StandardError):
    pass


def select_substances(query):
    headers = list(query('tr > th').map(lambda i, v: PyQuery(v).text()))[1:]

    def parse_substance_header(header):
        match = SUBSTANCE_RE.search(header)
        if not match:
            raise ParseSubstanceHeaderError("header doesn't match regexp")
        return Substance(name=match.group('name').replace('PM25', 'PM2.5'),
                         alias=match.group('alias') or '')

    result = []
    for index, header in enumerate(headers):
        substance = parse_substance_header(header)
        result.append(substance)
        repeats = int(query('tr > th:nth-child(%d)' % (index + 2))
                      .attr('colspan') or 1)
        result += [substance] * (repeats - 1)
    return result


def select_units(query):
    return list(query('tr > td[class=header]')
                .map(lambda i, v: PyQuery(v).text()))


def select_performed(query):
    headers = list(query('tr > td:first-child')
                   .map(lambda i, v: PyQuery(v).text()))[1:]
    temp = {'last': datetime.now()}

    def convert_header(header):
        try:
            result = datetime.strptime(header, FULL_DATETIME_FORMAT)
            temp['last'] = temp['last'].replace(
                year=result.year, month=result.month, day=result.day)
            return result
        except ValueError:
            result = datetime.strptime(header, SHORT_DATETIME_FORMAT)
            return result.replace(year=temp['last'].year,
                                  month=temp['last'].month,
                                  day=temp['last'].day)

    return [convert_header(h) for h in headers]


def select_measurements(query, substances, units, performed):
    def make_measurement(i, j, value):
        value = PyQuery(value).text()
        return Measurement(
            substance=substances[j].name,
            unit=units[j],
            performed=performed[i],
            value=None if value == u'—' else float(value))

    result = []
    (query('tr').filter(lambda i: i >= 2).map(
        lambda i, v: (PyQuery(v)('td').filter(lambda j: j >= 1)).each(
            lambda j, v: result.append(make_measurement(i, j, v)))))
    return result


def select_station_alias(query):
    match = STATION_ALIAS_RE.search(query('caption').text())
    if not match:
        return ''
    return match.group('alias').replace(u'\xa0', ' ')


def parse_table(table_html):
    query = PyQuery(table_html)
    substances = select_substances(query)
    units = select_units(query)
    performed = select_performed(query)
    measurements = select_measurements(query, substances, units, performed)
    station_alias = select_station_alias(query)
    return (measurements, sorted(list(set(substances))),
            sorted(list(set(units))), station_alias)


def parse(html):
    table_html = get_table_html(html)
    measurements, substances, units, station_alias = parse_table(table_html)
    return Result(measurements=measurements, substances=substances,
                  units=units, station_alias=station_alias)
