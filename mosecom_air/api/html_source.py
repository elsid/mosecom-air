# coding: utf-8

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

    def __init__(self, host=None, user_agent=None):
        self.headers = {'User-Agent': user_agent or self.USER_AGENT}
        self.__connection = HTTPConnection(host or self.HOST)

    def request(self, url):
        self.__connection.request('GET', url, headers=self.headers)
        response = self.__connection.getresponse()
        if response.status != OK:
            raise RequestError('reason=[request error] url=[%s] status=[%d]'
                               % (url, response.status))
        return response.read()

    def get_stations_list(self):
        response = self.request(self.BASE_URL).decode(self.ENCODING)
        return list(PyQuery(response)('a')
                    .map(lambda i, v: PyQuery(v).attr('href'))
                    .filter(lambda i, v: v.startswith(self.STATION_URL_PREFIX))
                    .map(lambda i, v: v.replace(self.STATION_URL_PREFIX, '')))

    def get_station_html(self, station):
        return self.request(join(self.STATION_URL_PREFIX, station, self.TABLE))
