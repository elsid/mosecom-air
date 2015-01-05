#coding: utf-8

import simplejson as json
import urllib

from django.core.exceptions import ObjectDoesNotExist
from django.http import (HttpResponseServerError, HttpResponseBadRequest,
    HttpResponseNotFound)
from django import forms
from django.db.models import Min, Max
from django.views.decorators.gzip import gzip_page
from django.views.decorators.cache import cache_page

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, BaseRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from mosecom_air import settings

from mosecom_air.api.add import add as add_data
from mosecom_air.api.json_parser import parse as parse_json
from mosecom_air.api.models import *
from mosecom_air.api.update import update as update_data
from mosecom_air.api.log import make_logger

cache_page = cache_page(settings.CACHES['default']['TIMEOUT'])

class InvalidForm(StandardError):
    MESSAGE = 'invalid request parameters'

    def __init__(self, errors):
        self.errors = dict(errors)
        super(InvalidForm, self).__init__(self.MESSAGE)

def validate_form(form):
    if not form.is_valid():
        raise InvalidForm(form.errors)
    return form

class PlainTextRenderer(BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        return str(data).encode(self.charset)

@make_logger
@api_view(('GET',))
@renderer_classes((PlainTextRenderer,))
def ping(request, logger):
    try:
        return Response('pong')
    except Exception as error:
        logger.error('reason=[%s]', error)
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@make_logger
@cache_page
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def stations(request, logger, substance=None):
    try:
        stations = Station.objects.all()
        if substance is not None:
            substance = urllib.unquote(substance.encode('utf-8')).decode('utf-8')
            substance = Substance.objects.get(name=substance)
            stations_ids = [station.id for station in stations
                if (Measurement.objects.filter(substance=substance,
                    station=station).exists())]
            stations = Station.objects.filter(id__in=stations_ids)
        return Response(dict(stations.values_list('name', 'alias')))
    except ObjectDoesNotExist as error:
        logger.warning('reason=[%s]', error)
        return HttpResponseNotFound(str(error), content_type='text/plain')
    except Exception as error:
        logger.error('reason=[%s]', error)
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@make_logger
@cache_page
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def substances(request, logger, station=None):
    try:
        substances = Substance.objects.all()
        if station is not None:
            station = Station.objects.get(name=station)
            substances_ids = [substance.id for substance in substances
                if (Measurement.objects.filter(substance=substance,
                    station=station).exists())]
            substances = Substance.objects.filter(id__in=substances_ids)
        return Response(dict(substances.values_list('name', 'alias')))
    except ObjectDoesNotExist as error:
        logger.warning('reason=[%s]', error)
        return HttpResponseNotFound(str(error), content_type='text/plain')
    except Exception as error:
        logger.error('reason=[%s]', error)
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@make_logger
@cache_page
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def units(request, logger):
    try:
        return Response(dict(Unit.objects.values_list()))
    except Exception as error:
        logger.error('reason=[%s]', error)
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

def mean(values):
    summa = 0
    length = 0
    for value in values:
        summa += value
        length += 1
    if length < 1:
        raise StandardError('mean requires at least one data point')
    return summa / float(length)

def last(values):
    result = None
    for value in values:
        result = value
    return result

class MeasurementsForm(forms.Form):
    FUNCTIONS = (
        ('min', min),
        ('mean', mean),
        ('max', max),
        ('first', next),
        ('last', last),
    )

    station = forms.CharField()
    substance = forms.CharField()
    unit = forms.IntegerField()
    start = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS)
    finish = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS)
    function = forms.ChoiceField(choices=FUNCTIONS)

@make_logger
@cache_page
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def measurements(request, logger):
    try:
        form = validate_form(MeasurementsForm(request.GET))
        data = form.cleaned_data
        station = Station.objects.get(name=data['station'])
        substance = Substance.objects.get(name=data['substance'])
        unit = Unit.objects.get(id=data['unit'])
        measurements = Measurement.objects.filter(station=station,
            substance=substance, unit=unit, performed__gte=data['start'],
            performed__lte=data['finish'])

        def make_apply(function):
            def _apply(performed):
                return function((m.value for m in
                    measurements.filter(performed=performed)))
            return _apply

        function = dict(form.fields['function'].choices)[data['function']]
        _apply = make_apply(function)
        performed_unique_values = set((m.performed for m in measurements))
        reduced = ((p, _apply(p)) for p in performed_unique_values)
        result = [{
                'performed': performed.isoformat(),
                'value': value,
            } for performed, value in reduced]
        return Response(result)
    except InvalidForm as error:
        logger.warning('reason=[%s]', error)
        return Response({'message': str(error), 'errors': error.errors},
                        status=HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist as error:
        logger.warning('reason=[%s]', error)
        return HttpResponseNotFound(str(error), content_type='text/plain')
    except Exception as error:
        logger.error('reason=[%s]', error)
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@make_logger
@gzip_page
@api_view(('GET',))
@renderer_classes((PlainTextRenderer,))
def update(request, logger):
    try:
        update_data(logger)
        return Response('done')
    except Exception as error:
        logger.error('reason=[%s]', error)
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

class AddForm(forms.Form):
    station = forms.CharField()
    json_data = forms.CharField()

@make_logger
@gzip_page
@api_view(('POST',))
@renderer_classes((PlainTextRenderer,))
def add(request, logger):
    try:
        form = validate_form(AddForm(request.POST))
        data = form.cleaned_data
        add_data(data['station'], parse_json(data['json_data']))
        return Response('done')
    except Exception as error:
        logger.error('reason=[%s]', error)
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@make_logger
@cache_page
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def interval(request, logger):
    try:
        interval = Measurement.objects.aggregate(start=Min('performed'),
                                                 finish=Max('performed'))
        return Response(interval)
    except ObjectDoesNotExist as error:
        logger.warning('reason=[%s]', error)
        return HttpResponseNotFound(str(error), content_type='text/plain')
    except Exception as error:
        logger.error('reason=[%s]', error)
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@make_logger
@cache_page
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def functions(request, logger):
    try:
        return Response(dict(MeasurementsForm.FUNCTIONS).keys())
    except Exception as error:
        logger.error('reason=[%s]', error)
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')
