#coding: utf-8

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

urlpatterns = patterns('',
    url(r'^api/', include('mosecom_air.api.urls')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
