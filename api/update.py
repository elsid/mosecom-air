#coding: utf-8

import logging

from multiprocessing import Process

from html_source import HtmlSource, RequestError
from html_parser import parse as parse_html
from api.add import add as add_data

logger = logging.getLogger(__name__)

def update():
    source = HtmlSource()

    for station_name in source.get_stations_list():
        try:
            html = source.get_station_html(station_name)
            data = parse_html(html)
            add_data(station_name, data)
            logger.info('result=[success] station=[%s]', station_name)
        except RequestError as error:
            logger.error('result=[fail] station=[%s] %s', station_name, error)
