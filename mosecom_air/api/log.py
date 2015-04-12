# coding: utf-8

import logging


class SetUuid(logging.Filter):
    def __init__(self, uuid):
        super(SetUuid, self).__init__()
        self.uuid = uuid

    def filter(self, record):
        record.uuid = self.uuid
        return True


def make_one_line(s):
    return str(s).replace('\n', '\\n').replace('\r', '\\r')


def make_logger(func):
    def wrapper(request, *args, **kwargs):
        logger = logging.getLogger('api.request')
        logger.addFilter(SetUuid(request.META['X-Request-UUID']))
        kwargs['logger'] = logger
        return func(request, *args, **kwargs)
    return wrapper
