# coding: utf8

from functools import partial

from django.conf import settings
from bitmapist import setup_redis, mark_event

from utils import get_id

__all__ = ['userid_counting']

host, port, db = settings.CACHES['statistics']['LOCATION'].split(':')
setup_redis('default', host, port, db=db)


def userid_counting(userid, apps_list, platform, channel):
    id = get_id(userid)
    mark_event('request', id)
    map(partial(add_app_statistics, id, platform, channel), apps_list or [])


def add_app_statistics(userid, platform, channel, app):
    appid = app.get('appid')
    version = app.get('version')
    mark_event('request:%s' % appid, userid)
    mark_event('request:{}:{}'.format(appid, version), userid)
    mark_event('request:{}:{}'.format(appid, platform), userid)
    mark_event('request:{}:{}'.format(appid, channel), userid)
    mark_event('request:{}:{}:{}'.format(appid, platform, version), userid)
