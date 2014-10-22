# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 Crystalnix Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""

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
