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

import os

from builtins import range

from functools import partial
from datetime import datetime, timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from bitmapist import (
    setup_redis, mark_event, unmark_event,
    WeekEvents, MonthEvents, DayEvents, HourEvents
)
import pytz

from omaha.utils import (
    get_id, is_new_install, valuedispatch,
    redis, get_platforms_by_appid
)
from omaha import parser
from omaha.models import (
    ACTIVE_USERS_DICT_CHOICES, Request, AppRequest,
    Os, Hw, Event, Version, Channel, Platform
)
from sparkle.models import SparkleVersion

__all__ = ['userid_counting', 'is_user_active']

setup_redis('default',
            settings.REDIS_STAT_HOST,
            settings.REDIS_STAT_PORT,
            db=settings.REDIS_STAT_DB,
            password=settings.REDIS_PASSWORD)


def userid_counting(userid, apps_list, platform, now=None):
    id = get_id(userid)
    mark_event('request', id, now=now)
    list(map(partial(add_app_statistics, id, platform, now=now), apps_list or []))


def add_app_statistics(userid, platform, app, now=None):
    mark = partial(mark_event, now=now)
    if not now:
        now = timezone.now()
    appid = app.get('appid')
    version = app.get('version')
    channel = parser.get_channel(app)
    events = app.findall('event')
    nextversion = app.get('nextversion')

    err_events = filter(lambda x: x.get('eventresult') not in ['1', '2', '3'], events)
    if err_events:
        return

    install_event = filter(lambda x: x.get('eventtype') == '2', events)
    if is_new_install(appid, userid):
        if install_event:
            mark('new_install:%s' % appid, userid)
            mark('new_install:{}:{}'.format(appid, platform), userid)
            redis.setbit("known_users:%s" % appid, userid, 1)
            mark('request:{}:{}'.format(appid, nextversion), userid, track_hourly=True)
            mark('request:{}:{}:{}'.format(appid, platform, nextversion), userid, track_hourly=True)
            mark('request:{}:{}:{}:{}'.format(appid, platform, channel, nextversion), userid, track_hourly=True)
            mark('request:{}:{}'.format(appid, channel), userid)
            return

    elif userid not in MonthEvents('new_install:{}:{}'.format(appid, platform), year=now.year, month=now.month):
        mark('request:%s' % appid, userid)
        mark('request:{}:{}'.format(appid, platform), userid)
        if nextversion:
            mark('request:{}:{}'.format(appid, nextversion), userid, track_hourly=True)
            mark('request:{}:{}:{}'.format(appid, platform, nextversion), userid, track_hourly=True)
            mark('request:{}:{}:{}:{}'.format(appid, platform, channel, nextversion), userid, track_hourly=True)

    uninstall_event = filter(lambda x: x.get('eventtype') == '4', events)
    if uninstall_event:
        mark('uninstall:%s' % appid, userid)
        mark('uninstall:{}:{}'.format(appid, platform), userid)
    update_event = filter(lambda x: x.get('eventtype') == '3', events)
    if update_event:
        unmark_event('request:{}:{}'.format(appid, version), userid, track_hourly=True)
        unmark_event('request:{}:{}:{}'.format(appid, platform, version), userid, track_hourly=True)
        unmark_event('request:{}:{}:{}:{}'.format(appid, platform, channel, version), userid, track_hourly=True)
        mark('request:{}:{}'.format(appid, nextversion), userid, track_hourly=True)
        mark('request:{}:{}:{}'.format(appid, platform, nextversion), userid, track_hourly=True)
        mark('request:{}:{}:{}:{}'.format(appid, platform, channel, nextversion), userid, track_hourly=True)
    else:
        mark('request:{}:{}'.format(appid, version), userid, track_hourly=True)
        mark('request:{}:{}:{}'.format(appid, platform, version), userid, track_hourly=True)
        mark('request:{}:{}:{}:{}'.format(appid, platform, channel, version), userid, track_hourly=True)
    mark('request:{}:{}'.format(appid, channel), userid)


def get_users_statistics_months(app_id, platform=None, year=None, start=1, end=12):
    now = timezone.now()
    if not year:
        year = now.year

    if platform:
        install_event_name = 'new_install:{}:{}'.format(app_id, platform)
        update_event_name = 'request:{}:{}'.format(app_id, platform)
        uninstall_event_name = 'uninstall:{}:{}'.format(app_id, platform)
    else:
        install_event_name = 'new_install:%s' % app_id
        update_event_name = 'request:%s' % app_id
        uninstall_event_name = 'uninstall:%s' % app_id

    installs_by_month = []
    updates_by_month = []
    uninstalls_by_month = []
    for m in range(start, end + 1):
        installs_by_month.append(MonthEvents(install_event_name, year, m))
        updates_by_month.append(MonthEvents(update_event_name, year, m))
        uninstalls_by_month.append(MonthEvents(uninstall_event_name, year, m))
    installs_data = [(datetime(year, start + i, 1).strftime("%Y-%m"), len(e)) for i, e in enumerate(installs_by_month)]
    updates_data = [(datetime(year, start + i, 1).strftime("%Y-%m"), len(e)) for i, e in enumerate(updates_by_month)]
    res = dict(new=installs_data, updates=updates_data)
    if platform != 'mac':
        uninstalls_data = [(datetime(year, start + i, 1).strftime("%Y-%m"), len(e)) for i, e in enumerate(uninstalls_by_month)]
        res.update(dict(uninstalls=uninstalls_data))
    return res


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


def get_channel_statistics(app_id, date=None):
    if not date:
        date = timezone.now()

    event_name = 'request:{}:{}'
    channels = [c.name for c in Channel.objects.all()]
    data = [(channel, len(MonthEvents(event_name.format(app_id, channel), date.year, date.month))) for channel in channels]
    data = filter(lambda x: x[1], data)
    return data


def get_users_versions_by_platform(app_id, platform, date):
    if platform == 'mac':
        versions = [str(v) for v in SparkleVersion.objects.filter_by_enabled(app_id=app_id).values_list('short_version', flat=True)]
    else:
        versions = [str(v) for v in Version.objects.filter_by_enabled(app__id=app_id, platform__name=platform).values_list('version', flat=True)]
    event_name = 'request:{}:{}:{}'
    data = [(v, len(MonthEvents(event_name.format(app_id, platform, v), date.year, date.month))) for v in versions]
    data = filter(lambda x: x[1], data)
    return dict(data)


def get_users_versions(app_id, date=None):
    if not date:
        date = timezone.now()

    platforms = Platform.objects.values_list('name', flat=True)
    data = dict()                   # try to move it in the separate function
    for platform in platforms:
        platform_data = get_users_versions_by_platform(app_id, platform, date)
        data.update({platform: platform_data})

    return data



def get_hourly_data_by_platform(app_id, end, n_hours, versions, platform, channel, tz='UTC'):
    def build_event_name(app_id, platform, channel, v):
        if channel:
            return "request:{}:{}:{}:{}".format(app_id, platform, channel, v)
        else:
            return "request:{}:{}:{}".format(app_id, platform, v)

    tzinfo = pytz.timezone(tz)
    start = end - timezone.timedelta(hours=n_hours)

    hours = [datetime(start.year, start.month, start.day, start.hour, tzinfo=pytz.UTC)
             + timezone.timedelta(hours=x) for x in range(1, n_hours + 1)]

    data = [(v, [[hour.astimezone(tzinfo).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                  len(HourEvents.from_date(build_event_name(app_id, platform, channel, v), hour))]
                 for hour in hours])
            for v in versions]
    data = filter(lambda version_data: sum([data[1] for data in version_data[1]]), data)
    return dict(data)


def get_daily_data_by_platform(app_id, end, n_days, versions, platform, channel):
    def build_event_name(app_id, platform, channel, v):
        if channel:
            return "request:{}:{}:{}:{}".format(app_id, platform, channel, v)
        else:
            return "request:{}:{}:{}".format(app_id, platform, v)

    start = end - timezone.timedelta(days=n_days)

    days = [start + timezone.timedelta(days=x) for x in range(0, n_days+1)]
    data = [(v, [[day.strftime("%Y-%m-%dT00:%M:%S.%fZ"),
                  len(DayEvents.from_date(build_event_name(app_id, platform, channel, v), day))]
                 for day in days])
            for v in versions]
    data = filter(lambda version_data: sum([data[1] for data in version_data[1]]), data)
    return dict(data)


def get_users_live_versions(app_id, start, end, channel, tz='UTC'):
    import logging
    logging.info("Getting active versions from DB")
    platforms = [x.name for x in get_platforms_by_appid(app_id)]
    versions = {}

    for platform in platforms:
        if platform == 'mac':
            platform_data = [str(v) for v in SparkleVersion.objects.filter(app_id=app_id).values_list('short_version', flat=True)]
        else:
            platform_data = [str(v) for v in Version.objects.filter(app__id=app_id, platform__name=platform).values_list('version', flat=True)]
        versions.update({platform: platform_data})

    logging.info("Getting statistics from Redis")
    if start < timezone.now() - timedelta(days=7):
        n_days = (end-start).days

        data = dict()
        for platform in platforms:
            platform_data = get_daily_data_by_platform(app_id, end, n_days, versions[platform], platform, channel)
            data.update({platform: platform_data})

    else:
        tmp_hours = divmod((end - start).total_seconds(), 60 * 60)
        n_hours = tmp_hours[0] + 1
        n_hours = int(n_hours)

        data = dict()
        for platform in platforms:
            platform_data = get_hourly_data_by_platform(app_id, end, n_hours, versions[platform], platform, channel, tz=tz)
            data.update({platform: platform_data})
    return data


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
        kwargs['tag'] = parser.get_channel(app)
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
