#coding: utf-8

import simplejson as json

from dateutil.parser import parse as parse_datetime

from mosecom_air.api.parser import Substance, Measurement, Result

def make_measurements(data):
    return [Measurement(
        substance=value['substance'],
        unit=value['unit'],
        performed=parse_datetime(value['performed']),
        value=value['value']) for value in data]

def make_substances(data):
    return [Substance(name=value['name'], alias=value['alias'])
        for value in data]

def parse(json_data):
    data = json.loads(json_data)
    return Result(
        measurements=make_measurements(data['measurements']),
        substances=make_substances(data['substances']),
        units=data['units'],
        station_alias=data['station_alias'],)
