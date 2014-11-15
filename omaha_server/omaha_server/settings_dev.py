# coding: utf8

from settings_prod import *


INSTALLED_APPS += (
    'httplog',
)

MIDDLEWARE_CLASSES += (
    'httplog.middleware.RequestResponseLoggingMiddleware',
)

HTTPLOG_URLNAMES = ['update', 'sparkle_appcast']

SUIT_CONFIG['MENU'] = SUIT_CONFIG['MENU'] + (
    {'app': 'httplog', 'label': 'httplog', 'icon': 'icon-search'},
)
