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

from builtins import range

from functools import partial
from datetime import datetime, timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from bitmapist import setup_redis, mark_event, WeekEvents, MonthEvents, DayEvents

from omaha.utils import get_id, valuedispatch
from omaha.settings import DEFAULT_CHANNEL
from omaha.models import ACTIVE_USERS_DICT_CHOICES, Request, AppRequest, Os, Hw, Event, Version, Channel

__all__ = ['userid_counting', 'is_user_active']

host, port, db = settings.CACHES['statistics']['LOCATION'].split(':')
setup_redis('default', host, port, db=db)


def userid_counting(userid, apps_list, platform, now=None):
    id = get_id(userid)
    mark_event('request', id, now=now)
    list(map(partial(add_app_statistics, id, platform, now=now), apps_list or []))


def add_app_statistics(userid, platform, app, now=None):
    mark = partial(mark_event, now=now)
    appid = app.get('appid')
    version = app.get('version')
    channel = app.get('tag') or DEFAULT_CHANNEL
    mark('request:%s' % appid, userid)
    mark('request:{}:{}'.format(appid, version), userid)
    mark('request:{}:{}'.format(appid, platform), userid)
    mark('request:{}:{}'.format(appid, channel), userid)
    mark('request:{}:{}:{}'.format(appid, platform, version), userid)


def get_users_statistics_months(app_id=None):
    now = timezone.now()
    year = now.year
    event_name = 'request:%s' % app_id if app_id else 'request'

    months = []
    for m in range(1, 13):
        months.append(MonthEvents(event_name, year, m))
    data = [(datetime(year, i+1, 1).strftime("%B"), len(e)) for i, e in enumerate(months)]
    return data


def get_users_statistics_weeks(app_id=None):
    now = timezone.now()
    event_name = 'request:%s' % app_id if app_id else 'request'
    year = now.year
    current_week = now.isocalendar()[1]
    previous_week = (now - timedelta(weeks=1)).isocalendar()[1]
    yesterday = now - timedelta(days=1)
    data = [
        ('Previous week', len(WeekEvents(event_name, year, previous_week))),
        ('Current week', len(WeekEvents(event_name, year, current_week))),
        ('Yesterday', len(DayEvents(event_name, year, yesterday.month, yesterday.day))),
        ('Today', len(DayEvents(event_name, year, now.month, now.day))),
    ]
    return data


def get_channel_statistics(app_id):
    now = timezone.now()
    event_name = 'request:{}:{}'
    week = now.isocalendar()[1]
    channels = [c.name for c in Channel.objects.all()]
    data = [(channel, len(WeekEvents(event_name.format(app_id, channel), now.year, week))) for channel in channels]
    return data


def get_users_versions(app_id):
    now = timezone.now()
    event_name = 'request:{}:{}'
    week = now.isocalendar()[1]
    versions = [str(v.version) for v in Version.objects.filter_by_enabled(app__id=app_id)]
    data = [(v, len(WeekEvents(event_name.format(app_id, v), now.year, week))) for v in versions]
    return filter(lambda x: x[1], data)


@valuedispatch
def is_user_active(period, userid):
    return False


@is_user_active.register(ACTIVE_USERS_DICT_CHOICES['all'])
def _(period, userid):
    return True


@is_user_active.register(ACTIVE_USERS_DICT_CHOICES['week'])
def _(period, userid):
    return get_id(userid) in WeekEvents.from_date('request', timezone.now())


@is_user_active.register(ACTIVE_USERS_DICT_CHOICES['month'])
def _(period, userid):
    return get_id(userid) in MonthEvents.from_date('request', timezone.now())


def get_kwargs_for_model(cls, obj, exclude=None):
    exclude = exclude or []
    fields = [(field.name, field.to_python) for field in cls._meta.fields if field.name not in exclude]
    kwargs = dict([(i, convert(obj.get(i))) for (i, convert) in fields])
    return kwargs


def parse_os(os):
    kwargs = get_kwargs_for_model(Os, os, exclude=['id'])
    obj, flag = Os.objects.get_or_create(**kwargs)
    return obj


def parse_hw(hw):
    kwargs = get_kwargs_for_model(Hw, hw, exclude=['id'])
    obj, flag = Hw.objects.get_or_create(**kwargs)
    return obj


def parse_req(request, ip=None):
    kwargs = get_kwargs_for_model(Request, request, exclude=['os', 'hw', 'created', 'id'])
    kwargs['ip'] = ip
    return Request(**kwargs)


def parse_apps(apps, request):
    app_list = []
    for app in apps:
        events = app.findall('event')

        if not events:
            continue

        kwargs = get_kwargs_for_model(AppRequest, app, exclude=['request', 'version', 'nextversion', 'id'])
        kwargs['version'] = app.get('version') or None
        kwargs['nextversion'] = app.get('nextversion') or None
        app_req = AppRequest.objects.create(request=request, **kwargs)
        event_list = parse_events(events)
        app_req.events.add(*event_list)
        app_list.append(app_req)
    return app_list


def parse_events(events):
    res = []
    for event in events:
        kwargs = get_kwargs_for_model(Event, event)
        res.append(Event.objects.create(**kwargs))
    return res


@transaction.atomic
def collect_statistics(request, ip=None):
    userid = request.get('userid')
    apps = request.findall('app')

    if userid:
        userid_counting(userid, apps, request.os.get('platform'))

    if not filter(lambda app: bool(app.findall('event')), apps):
        return

    req = parse_req(request, ip)
    req.os = parse_os(request.os)
    req.hw = parse_hw(request.hw) if request.get('hw') else None
    req.save()

    parse_apps(apps, req)

