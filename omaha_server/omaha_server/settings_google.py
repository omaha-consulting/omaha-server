import os

from .settings_prod import *

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
PUBLIC_READ_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATIC_URL = '/static/'

GS_AUTO_CREATE_BUCKET = True
GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME', 'omaha-server')
GS_PROJECT_ID = os.environ.get('GS_PROJECT_ID')
GS_AUTO_CREATE_ACL = 'publicRead'
