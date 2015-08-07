# coding: utf-8

from logging import getLogger, LoggerAdapter


def make_one_line(s):
    return str(s).replace('\n', '\\n').replace('\r', '\\r')


def make_logger(func):
    def wrapper(request, *args, **kwargs):
        uuid = request.META['X-Request-UUID']
        logger = getLogger('api.request')
        adapter = LoggerAdapter(logger, dict(uuid=uuid))
        kwargs['logger'] = adapter
        return func(request, *args, **kwargs)
    return wrapper
