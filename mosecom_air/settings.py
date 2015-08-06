# coding: utf-8

import yaml

from os.path import dirname, join
from sys import argv
from datetime import timedelta

CONFIG_FILE = '/etc/mosecom-air.conf'
CONFIG = yaml.load(open(CONFIG_FILE))
BASE_DIR = dirname(__file__)
SECRET_KEY = CONFIG['secret_key']
DEBUG = CONFIG['debug']
TEMPLATE_DEBUG = CONFIG['template_debug']
ALLOWED_HOSTS = CONFIG['allowed_hosts']

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'mosecom_air.api',
)

ROOT_URLCONF = 'mosecom_air.urls'
WSGI_APPLICATION = 'mosecom_air.wsgi.application'

if 'test' in argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test_mosecom_air',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': CONFIG['database']['name'],
            'USER': CONFIG['database']['user'],
            'PASSWORD': CONFIG['database']['password'],
            'HOST': CONFIG['database']['host'],
            'PORT': CONFIG['database']['port'],
            'JOHNNY_CACHE_KEY': 'default',
        }
    }

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = False
STATIC_ROOT = join(BASE_DIR, 'static')
STATIC_URL = '/'

DATETIME_INPUT_FORMATS = (
    '%Y-%m-%d', '%Y-%m-%dT%H', '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'request': {
            'format': '[%(asctime)s] [%(levelname)s] [%(uuid)s]: %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    'handlers': {
        'request': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'request'
        }
    },
    'loggers': {
        'api.request': {
            'handlers': ['request'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    }
}

MIDDLEWARE_CLASSES = (
    'johnny.middleware.QueryCacheMiddleware',
)

CACHES = {
    'default': {
        'BACKEND': 'johnny.backends.memcached.MemcachedCache',
        'LOCATION': CONFIG['cache']['location'],
        'TIMEOUT':  CONFIG['cache']['timeout'],
        'JOHNNY_CACHE': True,
    }
}

MAX_MEASUREMENTS_INTERVAL = timedelta(hours=CONFIG['max_measurements_interval'])
