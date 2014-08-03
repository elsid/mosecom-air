#coding: utf-8

from django.db import models

class Substance(models.Model):
    name = models.TextField(unique=True, db_index=True)
    alias = models.TextField()

class Station(models.Model):
    name = models.TextField(unique=True, db_index=True)
    alias = models.TextField()

class Unit(models.Model):
    name = models.TextField(unique=True, db_index=True)

class Measurement(models.Model):
    station = models.ForeignKey(Station)
    substance = models.ForeignKey(Substance)
    unit = models.ForeignKey(Unit)
    value = models.FloatField()
    performed = models.DateTimeField()
    written = models.DateTimeField(auto_now=True)
