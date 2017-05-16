# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2016 Crystalnix Limited

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

from bitmapist import mark_event, MonthEvents
from django.utils import timezone

from omaha.statistics import get_id, is_new_install, redis
from omaha.settings import DEFAULT_CHANNEL


def collect_statistics(request, appid, channel):
    deviceID = request.GET.get('deviceID')
    version = request.GET.get('appVersionShort')
    if not deviceID or not version:
        return
    app = dict(appid=appid,
               version=version,
               tag=channel)

    userid_counting(deviceID, app, 'mac')


def userid_counting(userid, app, platform, now=None):
    id = get_id(userid)
    mark_event('request', id, now=now)
    add_app_statistics(id, platform, app, now=now)


def add_app_statistics(userid, platform, app, now=None):
    mark = partial(mark_event, now=now)
    if not now:
        now = timezone.now()
    appid = app.get('appid')
    version = app.get('version')
    channel = app.get('tag') or DEFAULT_CHANNEL

    if is_new_install(appid, userid):
        mark('new_install:%s' % appid, userid)
        mark('new_install:{}:{}'.format(appid, platform), userid)
        redis.setbit("known_users:%s" % appid, userid, 1)
    elif userid not in MonthEvents('new_install:{}:{}'.format(appid, platform), year=now.year, month=now.month):
        mark('request:%s' % appid, userid)
        mark('request:{}:{}'.format(appid, platform), userid)

    mark('request:{}:{}'.format(appid, channel), userid)
    mark('request:{}:{}'.format(appid, version), userid, track_hourly=True)
    mark('request:{}:{}:{}'.format(appid, platform, version), userid, track_hourly=True)
    mark('request:{}:{}:{}:{}'.format(appid, platform, channel, version), userid, track_hourly=True)
