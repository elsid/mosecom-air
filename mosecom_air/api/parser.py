# coding: utf-8

from collections import namedtuple

Substance = namedtuple('Substance', ('name', 'alias'))
Measurement = namedtuple('Measurement', ('substance', 'unit', 'performed',
                                         'value'))
Result = namedtuple('Result', ('measurements', 'substances', 'units',
                               'station_alias'))
