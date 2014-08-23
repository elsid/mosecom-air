#coding: utf-8

import os
import sys
import yaml

CONFIG_FILE = '/etc/mosecom-air.conf'
CONFIG = yaml.load(open(CONFIG_FILE))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = CONFIG['secret_key']
DEBUG = CONFIG['debug']
TEMPLATE_DEBUG = CONFIG['template_debug']
ALLOWED_HOSTS = CONFIG['allowed_hosts']

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mosecom_air.api',
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
            'NAME': CONFIG['database']['name'],
            'USER': CONFIG['database']['user'],
            'PASSWORD': CONFIG['database']['password'],
            'HOST': CONFIG['database']['host'],
            'PORT': CONFIG['database']['port'],
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
