#coding: utf-8

from django.conf.urls import patterns, url
from mosecom_air.api import views

urlpatterns = patterns('',
    url(r'^add$', views.add, name='add'),
    url(r'^measurements$', views.measurements, name='measurements'),
    url(r'^ping$', views.ping, name='ping'),
    url(r'^stations$', views.stations, name='stations'),
    url(r'^substances$', views.substances, name='substances'),
    url(r'^units$', views.units, name='units'),
    url(r'^update$', views.update, name='update'),
    url(r'^stations/(?P<substance>.*)$', views.stations,
        name='stations_filtered_by_substance'),
    url(r'^substances/(?P<station>.*)$', views.substances,
        name='substances_filtered_by_station'),
    url(r'^interval$', views.interval, name='interval'),
)
