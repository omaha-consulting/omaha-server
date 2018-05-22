"""
Django settings for omaha_server project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from datetime import timedelta

from django.core.urlresolvers import reverse_lazy
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = BASE_DIR

IS_PRIVATE = True if os.getenv('OMAHA_SERVER_PRIVATE', '').title() == 'True' else False

RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DNS'),
}

if os.getenv('OMAHA_ONLY_HTTPS'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [
        r"^healthcheck/status/$"
    ]

SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': TCP + [
                'django.core.context_processors.request',
                'absolute.context_processors.absolute',
            ],
        },
    },
]

APP_VERSION = "0.6.6"

SUIT_CONFIG = {
    'ADMIN_NAME': 'Omaha Server [{}]'.format(APP_VERSION),
    'MENU': (
        # 'sites',
        {'app': 'omaha', 'label': 'Omaha', 'icon': 'icon-refresh'},
        {'app': 'sparkle', 'label': 'Sparkle', 'icon': 'icon-circle-arrow-down'},
        {'app': 'crash', 'label': 'Crash reports', 'icon': 'icon-fire'},
        {'app': 'feedback', 'label': 'Feedbacks', 'icon': 'icon-comment'},
        {'label': 'Statistics', 'url': 'omaha_statistics', 'icon': 'icon-star'},
        {'label': 'Preferences', 'url': reverse_lazy('set_preferences', args=['']), 'icon': 'icon-wrench'},
        {'label': 'Storage monitoring', 'url': 'monitoring', 'icon': 'icon-hdd'},
    ),
    'CONFIRM_UNSAVED_CHANGES': False,
}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qicy(##kk%%2%#5zyoz)&0*@2wlfis+6s*al2q3t!+#++(0%23'

HOST_NAME = os.environ.get('HOST_NAME')
OMAHA_URL_PREFIX = os.environ.get('OMAHA_URL_PREFIX') # no trailing slash!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'cacheops',
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'storages',
    'django_extensions',
    'versionfield',
    'absolute',
    'django_nvd3',
    'djangobower',
    'django_filters',
    'django_tables2',
    'django_ace',
    'rest_framework',
    'django_select2',
    'bootstrap3',
    'dynamic_preferences',

    'omaha',
    'crash',
    'feedback',
    'sparkle',
    'downloads',
    'healthcheck',
    'tinymce',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

if IS_PRIVATE:
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'omaha_server.middlewares.LoggingMiddleware',
        'omaha_server.middlewares.TimezoneMiddleware',
        'omaha_server.middlewares.CUP2Middleware',
    ) + MIDDLEWARE_CLASSES

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

DB_PUBLIC_ROLE = os.environ.get('DB_PUBLIC_ROLE', 'public_users')
DB_PUBLIC_USER = os.environ.get('DB_PUBLIC_USER', 'omaha_public')
DB_PUBLIC_PASSWORD = os.environ.get('DB_PUBLIC_PASSWORD', '')

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

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'assets'),
)

REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
REDIS_AUTH = 'redis://:{}@'.format(REDIS_PASSWORD) if REDIS_PASSWORD else ''

REDIS_STAT_PORT = os.environ.get('REDIS_STAT_PORT', REDIS_PORT)
REDIS_STAT_HOST = os.environ.get('REDIS_STAT_HOST', REDIS_HOST)
REDIS_STAT_DB = os.environ.get('REDIS_STAT_DB', 15)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '{REDIS_AUTH}{REDIS_HOST}:{REDIS_PORT}:{REDIS_DB}'.format(
            REDIS_AUTH=REDIS_AUTH,
            REDIS_PORT=REDIS_PORT,
            REDIS_HOST=REDIS_HOST,
            REDIS_DB=os.environ.get('REDIS_DB', 1)),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
    'statistics': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '{REDIS_AUTH}{REDIS_HOST}:{REDIS_PORT}:{REDIS_DB}'.format(
            REDIS_AUTH=REDIS_AUTH,
            REDIS_PORT=REDIS_STAT_PORT,
            REDIS_HOST=REDIS_STAT_HOST,
            REDIS_DB=REDIS_STAT_DB),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_CACHE_ALIAS = 'default'

STATICFILES_FINDERS = ("django.contrib.staticfiles.finders.FileSystemFinder",
                       "django.contrib.staticfiles.finders.AppDirectoriesFinder",
                       "djangobower.finders.BowerFinder",)

BOWER_COMPONENTS_ROOT = os.path.join(PROJECT_DIR, 'assets', 'components')

BOWER_INSTALLED_APPS = (
    'd3#3.3.13',
    'nvd3#1.7.1',
    'bootstrap#3.3.5',
)


# Celery

from kombu import Queue

BROKER_URL = CELERY_RESULT_BACKEND = '{}{}:{}/{}'.format(REDIS_AUTH or 'redis://', REDIS_HOST, REDIS_PORT, 3)
CELERY_DISABLE_RATE_LIMITS = True
CELERY_RESULT_SERIALIZER = 'msgpack'
CELERY_MESSAGE_COMPRESSION = 'zlib'
CELERY_QUEUES = (
    Queue('transient', routing_key='transient', delivery_mode=1),
    Queue('default', routing_key='default'),
)

if IS_PRIVATE:
    CELERY_QUEUES += (
        Queue('limitation', routing_key='limitation'),
        Queue('private', routing_key='private'),
    )

    CELERYBEAT_SCHEDULE = {
        'auto_delete_older_then': {
            'task': 'tasks.auto_delete_older_then',
            'schedule': timedelta(hours=24),
            'options': {'queue': 'limitation'},
        },
        'auto_delete_size_is_exceed': {
            'task': 'tasks.auto_delete_size_is_exceeded',
            'schedule': timedelta(hours=1),
            'options': {'queue': 'limitation'},
        },
        'auto_delete_duplicate_crashes': {
            'task': 'tasks.auto_delete_duplicate_crashes',
            'schedule': timedelta(hours=24),
            'options': {'queue': 'limitation'},
        },
        'auto_monitoring_size': {
            'task': 'tasks.auto_monitoring_size',
            'schedule': timedelta(seconds=60),
            'options': {'queue': 'limitation'},
        },
        'auto_delete_dangling_files': {
            'task': 'tasks.auto_delete_dangling_files',
            'schedule': timedelta(hours=24),
            'options': {'queue': 'limitation'},
        },
    }

# Cache

CACHEOPS_REDIS = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': 1,
    'socket_timeout': 3,
    'password': REDIS_PASSWORD or '',
}

CACHEOPS = {
    'omaha.*': {'ops': (), 'timeout': 10},
    'sparkle.*': {'ops': (), 'timeout': 10},
    'crash.*': {'ops': (), 'timeout': 10},
}

# Crash

CRASH_S3_MOUNT_PATH = os.environ.get('CRASH_S3_MOUNT_PATH', '/srv/omaha_s3')
CRASH_SYMBOLS_PATH = os.path.join(CRASH_S3_MOUNT_PATH, 'symbols')

# django-rest-framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
}

# django_select2

AUTO_RENDER_SELECT2_STATICS = False

# Client Update Protocol

CUP_REQUEST_VALIDATION = os.environ.get('CUP_REQUEST_VALIDATION', False)

CUP_PEM_KEYS = {
    # 'keyid': 'private_key_path',
}

CRASH_TRACKER = os.environ.get('CRASH_TRACKER', 'Sentry')

LOGSTASH_HOST = os.environ.get('LOGSTASH_HOST')
LOGSTASH_PORT = os.environ.get('LOGSTASH_PORT')

TINYMCE_BUTTONS = [
    'bold',
    'italic',
    'underline',
    'strikethrough',
    'separator',
    'bullist',
    'numlist',
    'outdent',
    'indent',
    'separator',
    'image',
    'media',
    'table',
    'link',
    'unlink',
    'separator',
    'forecolor',
    'backcolor',
    'separator',
    'hr',
]

TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'theme_advanced_buttons1': TINYMCE_BUTTONS,
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_toolbar_align': 'left',
    'paste_text_sticky': True,
    'paste_text_sticky_default': True,
    'plugins': 'table,media'
}