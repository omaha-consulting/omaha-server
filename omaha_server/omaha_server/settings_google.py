from .settings_prod import *

DEBUG = True

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'


STATIC_URL = '/static/'


GS_BUCKET_NAME = 'omaha-server-dev'
GS_PROJECT_ID = 'remarkable-nih-updateserver'
GS_AUTO_CREATE_ACL = 'publicRead'