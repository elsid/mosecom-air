#coding: utf-8

import logging

class RequestFilter(logging.Filter):
    def __init__(self, uuid):
        self.uuid = uuid

    def filter(self, record):
        record.uuid = self.uuid
        return True

def make_logger(func):
    def wrapper(request, *args, **kwargs):
        logger = logging.getLogger('api.request')
        logger.addFilter(RequestFilter(request.META['X-Request-UUID']))
        kwargs['logger'] = logger
        return func(request, *args, **kwargs)
    return wrapper
