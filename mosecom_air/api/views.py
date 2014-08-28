#coding: utf-8

import simplejson as json

from django.core.exceptions import ObjectDoesNotExist
from django.http import (HttpResponseServerError, HttpResponseBadRequest,
    HttpResponseNotFound)
from django import forms
from django.db.models import Min, Max

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, BaseRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from mosecom_air import settings

from mosecom_air.api.add import add as add_data
from mosecom_air.api.json_parser import parse as parse_json
from mosecom_air.api.models import *
from mosecom_air.api.update import update as update_data

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

@api_view(('GET',))
@renderer_classes((PlainTextRenderer,))
def ping(request):
    return Response('pong')

@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def stations(request, substance=None):
    try:
        if substance is None:
            stations = Station.objects.all()
        else:
            substance = Substance.objects.get(name=substance)
            stations_ids = (Measurement.objects.filter(substance=substance)
                .distinct('station').values_list('station', flat=True))
            stations = Station.objects.filter(id__in=stations_ids)
        return Response(dict(stations.values_list('name', 'alias')))
    except ObjectDoesNotExist as error:
        return HttpResponseNotFound(str(error), content_type='text/plain')
    except Exception as error:
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def substances(request, station=None):
    try:
        if station is None:
            substances = Substance.objects.all()
        else:
            station = Station.objects.get(name=station)
            substances_ids = (Measurement.objects.filter(station=station)
                .distinct('substance').values_list('substance', flat=True))
            substances = Substance.objects.filter(id__in=substances_ids)
        return Response(dict(substances.values_list('name', 'alias')))
    except ObjectDoesNotExist as error:
        return HttpResponseNotFound(str(error), content_type='text/plain')
    except Exception as error:
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def units(request):
    try:
        return Response(dict(Unit.objects.values_list()))
    except Exception as error:
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
    start = forms.DateTimeField()
    finish = forms.DateTimeField()
    function = forms.ChoiceField(choices=FUNCTIONS)

@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def measurements(request):
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
        return Response({'message': str(error), 'errors': error.errors},
                        status=HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist as error:
        return HttpResponseNotFound(str(error), content_type='text/plain')
    except Exception as error:
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@api_view(('GET',))
@renderer_classes((PlainTextRenderer,))
def update(request):
    try:
        update_data()
        return Response('done')
    except Exception as error:
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

class AddForm(forms.Form):
    station = forms.CharField()
    json_data = forms.CharField()

@api_view(('POST',))
@renderer_classes((PlainTextRenderer,))
def add(request):
    try:
        form = validate_form(AddForm(request.POST))
        data = form.cleaned_data
        add_data(data['station'], parse_json(data['json_data']))
        return Response('done')
    except Exception as error:
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def interval(request):
    try:
        interval = Measurement.objects.aggregate(start=Min('performed'),
                                                 finish=Max('performed'))
        return Response(interval)
    except ObjectDoesNotExist as error:
        return HttpResponseNotFound(str(error), content_type='text/plain')
    except Exception as error:
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')
