"""
Django settings for omaha_server project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = BASE_DIR

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    'absolute.context_processors.absolute',
)

SUIT_CONFIG = {
    'ADMIN_NAME': 'Omaha Server',
    'MENU': (
        'sites',
        {'app': 'omaha', 'label': 'Omaha', 'icon': 'icon-refresh'},
        {'app': 'crash', 'label': 'Crash reports', 'icon': 'icon-fire'},
        {'label': 'Statistics', 'url': 'omaha_statistics', 'icon': 'icon-star'},
    ),
}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qicy(##kk%%2%#5zyoz)&0*@2wlfis+6s*al2q3t!+#++(0%23'

HOST_NAME = os.environ['HOST_NAME']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'cacheops',
    'suit',
    'suit_redactor',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'storages',
    'django_extensions',
    'versionfield',
    'absolute',
    'django_nvd3',
    'djangobower',
    'django_filters',
    'django_tables2',
    'django_select2',
    'django_ace',

    'omaha',
    'crash',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'omaha_server.urls'

WSGI_APPLICATION = 'omaha_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
MEDIA_ROOT = os.path.join(STATIC_ROOT, 'media')

STATIC_URL = '/static/'
MEDIA_URL = '/static/media/'

REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '{REDIS_HOST}:{REDIS_PORT}:{REDIS_DB}'.format(
            REDIS_PORT=REDIS_PORT,
            REDIS_HOST=REDIS_HOST,
            REDIS_DB=os.environ.get('REDIS_DB', 1)),
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
        }
    },
    'statistics': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '{REDIS_HOST}:{REDIS_PORT}:{REDIS_DB}'.format(
            REDIS_PORT=os.environ.get('REDIS_STAT_PORT', REDIS_PORT),
            REDIS_HOST=os.environ.get('REDIS_STAT_HOST', REDIS_HOST),
            REDIS_DB=os.environ.get('REDIS_STAT_DB', 15)),
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

STATICFILES_FINDERS = ("django.contrib.staticfiles.finders.FileSystemFinder",
                       "django.contrib.staticfiles.finders.AppDirectoriesFinder",
                       "djangobower.finders.BowerFinder",)

BOWER_COMPONENTS_ROOT = os.path.join(PROJECT_DIR, 'assets', 'components')

BOWER_INSTALLED_APPS = (
    'd3#3.3.6',
    'nvd3#1.1.12-beta',
)


# Celery

from kombu import Queue

BROKER_URL = CELERY_RESULT_BACKEND = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, 3)
CELERY_DISABLE_RATE_LIMITS = True
CELERY_RESULT_SERIALIZER = 'msgpack'
CELERY_MESSAGE_COMPRESSION = 'zlib'
CELERY_QUEUES = (
    Queue('transient', routing_key='transient', delivery_mode=1),
    Queue('default', routing_key='default'),
)


# Cache

CACHEOPS_REDIS = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': 1,
    'socket_timeout': 3,
}

CACHEOPS = {
    'omaha.*': {'ops': (), 'timeout': 10},
}

# Crash

CRASH_S3_MOUNT_PATH = os.environ.get('CRASH_S3_MOUNT_PATH', '/srv/omaha_s3')
CRASH_SYMBOLS_PATH = os.path.join(CRASH_S3_MOUNT_PATH, 'symbols')
