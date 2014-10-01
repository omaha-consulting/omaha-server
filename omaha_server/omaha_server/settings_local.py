# coding: utf8

from settings import *

DEBUG = True

ALLOWED_HOSTS = ('localhost', '127.0.0.1', 'xip.io', '.xip.io',)

SUIT_CONFIG = {
    'ADMIN_NAME': 'Omaha Server - local',
}

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATIC_URL = '/static/'

STATICFILES_FINDERS = ("django.contrib.staticfiles.finders.FileSystemFinder",
                       "django.contrib.staticfiles.finders.AppDirectoriesFinder")

SITE_ID = 1