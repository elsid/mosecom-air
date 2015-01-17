#!/usr/bin/env python
#coding: utf-8

import sys

from argparse import ArgumentParser

from mosecom_air.api.html_source import HtmlSource

def make_args_parser():
    parser = ArgumentParser(description='Request data from mosecom.ru')
    parser.add_argument('data', choices=('stations_list', 'station_html'),
        help=('stations_list - list of stations names, each on separate line\n'
            + 'station_html - html page for specific station'))
    parser.add_argument('station_name', nargs='?', default=None,
        help='argument for station_html')
    parser.add_argument('-H', '--host', default=None)
    parser.add_argument('-u', '--user_agent', default=None)
    return parser

def parse_args():
    return make_args_parser().parse_args()

if __name__ == '__main__':
    args = parse_args()
    source = HtmlSource(args.host, args.user_agent)

    def stations_list():
        for station_name in source.get_stations_list():
            print station_name

    def station_html(station):
        sys.stdout.write(source.get_station_html(station))

    {
        'stations_list': stations_list,
        'station_html': lambda: station_html(args.station_name),
    }[args.data]()
