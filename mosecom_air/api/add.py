#coding: utf-8

from django.db import transaction, IntegrityError

from mosecom_air.api.models import Substance, Station, Unit, Measurement

def add_station(name, alias):
    try:
        Station(name=name, alias=alias).save()
    except IntegrityError:
        pass

def add_substance(substance):
    try:
        Substance(name=substance.name, alias=substance.alias).save()
    except IntegrityError:
        pass

def add_substances(substances):
    for substance in substances:
        add_substance(substance)

def add_unit(unit):
    try:
        Unit(name=unit).save()
    except IntegrityError:
        pass

def add_units(units):
    for unit in units:
        add_unit(unit)

def add_measurement(station, measurement):
    return Measurement(
        station=station,
        substance=Substance.objects.get(name=measurement.substance),
        unit=Unit.objects.get(name=measurement.unit),
        performed=measurement.performed,
        value=measurement.value).save()

@transaction.commit_on_success
def add_measurements(station_name, measurements):
    station = Station.objects.get(name=station_name)
    for measurement in measurements:
        if measurement.value is not None:
            add_measurement(station, measurement)

def add(station_name, data):
    add_station(station_name, data.station_alias)
    add_substances(data.substances)
    add_units(data.units)
    add_measurements(station_name, data.measurements)
