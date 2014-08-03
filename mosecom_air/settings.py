#coding: utf-8

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = 'j5-eRz6L2_NjVJr_Qb9YcfqXdDh5nh5WCjhNYSjF47D__Yrt!1H_Peg3zt!75xbofcRFfYjEhqF47ZDJDf-sAi4AxhUFIQLcei-3LwIL7t1rRhJcYfwn8TU!5rSTYWSh'
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mosecom_air.urls'
WSGI_APPLICATION = 'mosecom_air.wsgi.application'

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE':'django.db.backends.sqlite3',
            'NAME': 'test_mosecom_air',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE':'django.db.backends.postgresql_psycopg2',
            'NAME': 'mosecom_air',
            'USER': 'mosecom_air',
            'PASSWORD': 'oKzO-9s4kcvZNqV9',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = False
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(levelname)s] [%(asctime)s] %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'api.update': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}
