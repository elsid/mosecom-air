# coding: utf-8

import os

from datetime import datetime
from django.test import TestCase

from mosecom_air.settings import BASE_DIR
from mosecom_air.api.parser import Result, Substance, Measurement
from mosecom_air.api.html_parser import parse as parse_html
from mosecom_air.api.json_parser import parse as parse_json


class Parser(TestCase):
    VALID_SOURCE = None
    VALID_DATA = Result(
        station_alias=u'Марьинский парк',
        units=sorted(list({u'мг / куб. м', u'единицы ПДК м.р.'})),
        substances=sorted(list({
            Substance(name=u'CH4', alias=u'Метан'),
            Substance(name=u'CH-', alias=u'Неметановые углеводороды'),
        })),
        measurements=[
            Measurement(substance=u'CH4', unit=u'мг / куб. м',
                        performed=datetime(2014, 8, 1, 16), value=0.1),
            Measurement(substance=u'CH4', unit=u'единицы ПДК м.р.',
                        performed=datetime(2014, 8, 1, 16), value=0.2),
            Measurement(substance=u'CH-', unit=u'мг / куб. м',
                        performed=datetime(2014, 8, 1, 16), value=0.3),
            Measurement(substance=u'CH4', unit=u'мг / куб. м',
                        performed=datetime(2014, 8, 1, 17), value=1.1),
            Measurement(substance=u'CH4', unit=u'единицы ПДК м.р.',
                        performed=datetime(2014, 8, 1, 17), value=1.2),
            Measurement(substance=u'CH-', unit=u'мг / куб. м',
                        performed=datetime(2014, 8, 1, 17), value=1.3),
            Measurement(substance=u'CH4', unit=u'мг / куб. м',
                        performed=datetime(2014, 8, 2, 18), value=0),
            Measurement(substance=u'CH4', unit=u'единицы ПДК м.р.',
                        performed=datetime(2014, 8, 2, 18), value=0),
            Measurement(substance=u'CH-', unit=u'мг / куб. м',
                        performed=datetime(2014, 8, 2, 18), value=0),
            Measurement(substance=u'CH4', unit=u'мг / куб. м',
                        performed=datetime(2014, 8, 2, 19), value=1),
            Measurement(substance=u'CH4', unit=u'единицы ПДК м.р.',
                        performed=datetime(2014, 8, 2, 19), value=2),
            Measurement(substance=u'CH-', unit=u'мг / куб. м',
                        performed=datetime(2014, 8, 2, 19), value=3),
            Measurement(substance=u'CH4', unit=u'мг / куб. м',
                        performed=datetime(2014, 8, 2, 20), value=10),
            Measurement(substance=u'CH4', unit=u'единицы ПДК м.р.',
                        performed=datetime(2014, 8, 2, 20), value=20),
            Measurement(substance=u'CH-', unit=u'мг / куб. м',
                        performed=datetime(2014, 8, 2, 20), value=30),
        ]
    )

    def parse(self, data):
        raise NotImplementedError()

    def test_details(self):
        source = open(self.VALID_SOURCE).read()
        self.assertEqual(self.parse(source), self.VALID_DATA)


class HtmlParser(Parser):
    VALID_SOURCE = os.path.join(BASE_DIR, 'mosecom_air/api/test/valid.html')

    def parse(self, html):
        return parse_html(html)


class JsonParser(Parser):
    VALID_SOURCE = os.path.join(BASE_DIR, 'mosecom_air/api/test/valid.json')

    def parse(self, json):
        return parse_json(json)
