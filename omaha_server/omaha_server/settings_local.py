# coding: utf8

from .settings import *

DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ('localhost', '127.0.0.1', '.xip.io',)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATIC_URL = '/static/'

SITE_ID = 1

# INSTALLED_APPS += (
#     'debug_toolbar',
#     'debug_panel',
# )

# MIDDLEWARE += (
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# )

#
# Debug Toolbar
#

# DEBUG_TOOLBAR_PANELS = (
#     'debug_toolbar.panels.versions.VersionsPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     'debug_toolbar.panels.settings.SettingsPanel',
#     'debug_toolbar.panels.headers.HeadersPanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.signals.SignalsPanel',
#     'debug_toolbar.panels.logging.LoggingPanel',
#     'debug_toolbar.panels.redirects.RedirectsPanel',
# )

# IGNORED_TEMPLATES = ["debug_toolbar/*"]  # Ignore these templates from the output
# DEBUG_TOOLBAR_PATCH_SETTINGS = False

# DEBUG_TOOLBAR_CONFIG = {
#     'INTERCEPT_REDIRECTS': False,
#     'SHOW_TOOLBAR_CALLBACK': 'omaha_server.utils.show_toolbar',
# }


CRASH_S3_MOUNT_PATH = os.environ.get('CRASH_S3_MOUNT_PATH', BASE_DIR)
CRASH_SYMBOLS_PATH = os.path.join(CRASH_S3_MOUNT_PATH, os.path.join(MEDIA_ROOT, 'symbols'))
