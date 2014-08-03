#coding: utf-8

from django.conf.urls import patterns, url
from api import views

urlpatterns = patterns('',
    url(r'^add', views.add, name='add'),
    url(r'^measurements', views.measurements, name='measurements'),
    url(r'^ping', views.ping, name='ping'),
    url(r'^stations', views.stations, name='stations'),
    url(r'^substances', views.substances, name='substances'),
    url(r'^units', views.units, name='units'),
    url(r'^update', views.update, name='update'),

)
