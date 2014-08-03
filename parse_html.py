#!/usr/bin/env python
#coding: utf-8

import simplejson as json
import sys

from argparse import ArgumentParser, FileType
from datetime import datetime

from api.html_parser import parse

def make_args_parse():
    parser = ArgumentParser(description='Parse html with measurements from '
        + 'mosecom.ru into json')
    parser.add_argument('file', type=FileType('r'), nargs='?',
        default=sys.stdin)
    return parser

def parse_args():
    return make_args_parse().parse_args()

class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return super(DateTimeJSONEncoder, self).default(obj)

if __name__ == '__main__':
    args = parse_args()
    json.dump(parse(args.file.read()), sys.stdout, cls=DateTimeJSONEncoder,
        encoding='utf-8')
