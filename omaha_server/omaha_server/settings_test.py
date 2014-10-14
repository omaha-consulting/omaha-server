# coding: utf8

from .settings import *

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

INSTALLED_APPS += (
    'django_nose',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=omaha_server,omaha',
    '--cover-inclusive',
    '--with-doctest',
]

# Tricks to speed up Django tests

DEBUG = False
TEMPLATE_DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_db',
    }
}
SOUTH_TESTS_MIGRATE = False
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'

CACHES = {
    "default": {
        "BACKEND": 'django.core.cache.backends.locmem.LocMemCache',
    }
}