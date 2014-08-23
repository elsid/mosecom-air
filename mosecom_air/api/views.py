#coding: utf-8

import simplejson as json

from django.core.exceptions import ObjectDoesNotExist
from django.http import (HttpResponseServerError, HttpResponseBadRequest,
    HttpResponseNotFound)
from django import forms
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, BaseRenderer
from rest_framework.response import Response

from mosecom_air import settings

from mosecom_air.api.add import add as add_data
from mosecom_air.api.json_parser import parse as parse_json
from mosecom_air.api.models import *
from mosecom_air.api.update import update as update_data

class InvalidForm(StandardError):
    pass

def validate_form(form):
    if not form.is_valid():
        raise InvalidForm('invalid request parameters')
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
def stations(request):
    try:
        return Response([{'name': station.name, 'alias': station.alias}
            for station in Station.objects.all()])
    except Exception as error:
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def substances(request):
    try:
        return Response([{'name': substance.name, 'alias': substance.alias}
            for substance in Substance.objects.all()])
    except Exception as error:
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def units(request):
    try:
        return Response([{'name': unit.id, 'alias': unit.name}
            for unit in Unit.objects.all()])
    except Exception as error:
        if settings.DEBUG:
            raise
        return HttpResponseServerError(str(error), content_type='text/plain')

class SubstanceAliasForm(forms.Form):
    name = forms.CharField()

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
        return HttpResponseBadRequest(str(error), content_type='text/plain')
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
