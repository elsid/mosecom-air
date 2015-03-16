# coding: utf-8

import simplejson as json

from dateutil.parser import parse as parse_datetime

from mosecom_air.api.parser import Substance, Measurement, Result


class ParseError(StandardError):
    pass


def make_measurements(data):
    try:
        return [Measurement(
            substance=value['substance'],
            unit=value['unit'],
            performed=parse_datetime(value['performed']),
            value=value['value']) for value in data]
    except KeyError as error:
        raise ParseError("JSON parse error: no key %s in measurements" % error)


def make_substances(data):
    try:
        return [Substance(name=value['name'], alias=value['alias'])
                for value in data]
    except KeyError as error:
        raise ParseError("JSON parse error: no key %s in substances" % error)


def parse(json_data):
    try:
        data = json.loads(json_data)
        return Result(
            measurements=make_measurements(data['measurements']),
            substances=make_substances(data['substances']),
            units=data['units'],
            station_alias=data['station_alias'],)
    except KeyError as error:
        raise ParseError("JSON parse error: no key " + str(error))
