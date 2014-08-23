#coding: utf-8

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^api/', include('mosecom_air.api.urls')),
)
