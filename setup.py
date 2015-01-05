#!/usr/bin/env python
#coding: utf-8

from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='mosecom_air',
    version='1.6',
    description='Web service dedicated to air pollution in Moscow.',
    long_description=open('README.md').read(),
    author='elsid',
    author_email='elsid.mail@gmail.com',
    packages=find_packages(),
    scripts=['manage.py', 'parse_html.py', 'request.py'],
    install_requires=[
        'django >= 1.6.1',
        'djangorestframework >= 2.3.12',
        'flup >= 1.0.2',
        'johnny-cache >= 1.4',
        'memcache >= 1.53',
        'psycopg2 >= 2.4.5',
        'pyquery >= 1.2.4',
        'simplejson >= 3.3.1',
        'yaml >= 3.10',
    ],
)
