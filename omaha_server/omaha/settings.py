# coding: utf8

from django.conf import settings

KEY_PREFIX = getattr(settings, 'OMAHA_UID_KEY_PREFIX', 'uid')
KEY_LAST_ID = getattr(settings, 'OMAHA_KEY_LAST_ID', '{}:{}'.format(KEY_PREFIX, 'last_id'))