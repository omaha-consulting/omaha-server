# coding: utf8

from django.conf import settings
from bitmapist import setup_redis, mark_event

from utils import get_id

__all__ = ['userid_counting']

host, port, db = settings.CACHES['statistics']['LOCATION'].split(':')
setup_redis('default', host, port, db=db)


def userid_counting(userid, app_id_list):
    id = get_id(userid)
    mark_event('request', id)
    map(lambda i: mark_event('request:%s' % i, id),
        app_id_list or [])
