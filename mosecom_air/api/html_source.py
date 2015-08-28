# coding: utf-8

import re

from os.path import join
from httplib import HTTPConnection, OK
from pyquery import PyQuery


class RequestError(StandardError):
    pass


class HtmlSource(object):
    HOST = 'mosecom.ru'
    USER_AGENT = ('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 '
                  'Firefox/30.0')
    ENCODING = 'windows-1251'
    BASE_URL = '/air/air-today/'
    STATION_URL_PREFIX = '/air/air-today/station/'
    TABLE = 'table.html'
    STATION_NAME_RE = re.compile(STATION_URL_PREFIX + r'([^/]*)')

    def __init__(self, logger=None, host=None, user_agent=None):
        self.headers = {'User-Agent': (user_agent if user_agent is not None
                                       else self.USER_AGENT)}
        self.__logger = logger
        self.__host = host if host is not None else self.HOST

    def request(self, url):
        conn = HTTPConnection(self.__host)
        conn.request('GET', url, headers=self.headers)
        response = conn.getresponse()
        self._log(url, response)
        if response.status != OK:
            raise RequestError('reason=[request error] url=[%s] status=[%d]'
                               % (url, response.status))
        return response.read()

    def get_stations_list(self):
        response = self.request(self.BASE_URL).decode(self.ENCODING)
        return list(PyQuery(response)('a')
                    .map(lambda i, v: PyQuery(v).attr('href'))
                    .filter(lambda i, v: v.startswith(self.STATION_URL_PREFIX))
                    .map(lambda i, v: self.STATION_NAME_RE.match(v).group(1)))

    def get_station_html(self, station):
        return self.request(join(self.STATION_URL_PREFIX, station, self.TABLE))

    def _log(self, url, response):
        if self.__logger:
            self.__logger.info('action=[request] host=[%s] url=[%s] '
                               'status=[%s]', self.__host, url, response.status)
