# coding: utf-8

import urllib

from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.db.models import Min, Max
from django.views.decorators.gzip import gzip_page
from django.views.decorators.cache import cache_page

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from mosecom_air import settings

from mosecom_air.api.add import add as add_data
from mosecom_air.api.json_parser import parse as parse_json
from mosecom_air.api.models import *
from mosecom_air.api.update import update as update_data
from mosecom_air.api.log import make_logger, make_one_line

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


def handle_exception(logger, error):
    logger.error('class=[%s] reason=[%s]', type(error).__name__,
                 make_one_line(error))
    if settings.DEBUG:
        raise error
    return Response({'status': 'error', 'message': 'internal error'})


def handle_object_does_not_exists(logger, error):
    logger.warning('class=[%s] reason=[%s]', type(error).__name__,
                   make_one_line(error))
    return Response({'status': 'error', 'message': str(error)})


def handle_invalid_form(logger, error):
    logger.warning('class=[%s] reason=[%s]', type(error).__name__,
                   make_one_line(error))
    return Response({'status': 'error', 'message': str(error),
                     'errors': error.errors})


@make_logger
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def ping(_, logger):
    try:
        return Response({'status': 'ok'})
    except Exception as error:
        return handle_exception(logger, error)


@make_logger
@cache_page
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def stations(_, logger, substance=None):
    try:
        stations = Station.objects.all()
        if substance is not None:
            substance = (urllib.unquote(substance.encode('utf-8'))
                         .decode('utf-8'))
            substance = Substance.objects.get(name=substance)
            stations_ids = [
                x.station_id for x in
                StationsWithSubstances.objects.filter(substance=substance)]
            stations = Station.objects.filter(id__in=stations_ids)
        return Response(dict(stations.values_list('name', 'alias')))
    except ObjectDoesNotExist as error:
        return handle_object_does_not_exists(logger, error)
    except Exception as error:
        return handle_exception(logger, error)


@make_logger
@cache_page
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def substances(_, logger, station=None):
    try:
        substances = Substance.objects.all()
        if station is not None:
            station = Station.objects.get(name=station)
            substances_ids = [
                x.substance_id for x in
                StationsWithSubstances.objects.filter(station=station)]
            substances = Substance.objects.filter(id__in=substances_ids)
        return Response(dict(substances.values_list('name', 'alias')))
    except ObjectDoesNotExist as error:
        return handle_object_does_not_exists(logger, error)
    except Exception as error:
        return handle_exception(logger, error)


@make_logger
@cache_page
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def units(_, logger):
    try:
        return Response(dict(Unit.objects.values_list()))
    except Exception as error:
        return handle_exception(logger, error)


def mean(values):
    amount = 0
    length = 0
    for value in values:
        amount += value
        length += 1
    if length < 1:
        raise StandardError('mean requires at least one data point')
    return amount / float(length)


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
        max_interval = settings.MAX_MEASUREMENTS_INTERVAL
        if data['finish'] - data['start'] > max_interval:
            return Response({
                'status': 'error',
                'message': 'requested interval greater than %s hours'
                           % int(max_interval.total_seconds() / 3600)
            })
        station = Station.objects.get(name=data['station'])
        substance = Substance.objects.get(name=data['substance'])
        unit = Unit.objects.get(id=data['unit'])
        measurements = Measurement.objects.filter(
            station=station, substance=substance, unit=unit,
            performed__gte=data['start'], performed__lte=data['finish'])
        function = dict(form.fields['function'].choices)[data['function']]
        performed_unique_values = set((m.performed for m in measurements))
        reduced = (
            (x, function((m.value for m in measurements.filter(performed=x))))
            for x in performed_unique_values
        )
        result = [
            {
                'performed': performed.isoformat(),
                'value': value,
            } for performed, value in sorted(reduced, key=lambda p: p[0])]
        return Response(result)
    except InvalidForm as error:
        return handle_invalid_form(logger, error)
    except ObjectDoesNotExist as error:
        return handle_object_does_not_exists(logger, error)
    except Exception as error:
        return handle_exception(logger, error)


@make_logger
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def update(_, logger):
    try:
        update_data(logger)
        return Response({'status': 'done'})
    except Exception as error:
        return handle_exception(logger, error)


class AddForm(forms.Form):
    station = forms.CharField()
    json_data = forms.CharField()


@make_logger
@gzip_page
@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def add(request, logger):
    try:
        form = validate_form(AddForm(request.POST))
        data = form.cleaned_data
        add_data(data['station'], parse_json(data['json_data']))
        return Response({'status': 'done'})
    except InvalidForm as error:
        return handle_invalid_form(logger, error)
    except Exception as error:
        return handle_exception(logger, error)


@make_logger
@cache_page
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def interval(_, logger):
    try:
        result = Measurement.objects.aggregate(start=Min('performed'),
                                               finish=Max('performed'))
        return Response(result)
    except ObjectDoesNotExist as error:
        return handle_object_does_not_exists(logger, error)
    except Exception as error:
        return handle_exception(logger, error)

FUNCTIONS = {
    'first': 'Первое',
    'last': 'Последнее',
    'max': 'Максимальное',
    'mean': 'Среднее',
    'min': 'Минимальное',
}


@make_logger
@cache_page
@gzip_page
@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def functions(_, logger):
    try:
        return Response(FUNCTIONS)
    except Exception as error:
        return handle_exception(logger, error)
