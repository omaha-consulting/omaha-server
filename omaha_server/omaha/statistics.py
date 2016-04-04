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
from bitmapist import setup_redis, mark_event, unmark_event, WeekEvents, MonthEvents, DayEvents, HourEvents
import pytz

from omaha.utils import get_id, is_new_install, valuedispatch, redis
from omaha.settings import DEFAULT_CHANNEL
from omaha.models import ACTIVE_USERS_DICT_CHOICES, Request, AppRequest, Os, Hw, Event, Version, Channel
from sparkle.models import SparkleVersion

__all__ = ['userid_counting', 'is_user_active']

host, port, db = settings.CACHES['statistics']['LOCATION'].split(':')
setup_redis('default', host, port, db=db)


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
    channel = app.get('tag') or DEFAULT_CHANNEL

    if is_new_install(appid, userid):
        mark('new_install:%s' % appid, userid)
        mark('new_install:{}:{}'.format(appid, platform), userid)
        redis.setbit("known_users:%s" % appid, userid, 1)
    elif userid not in MonthEvents('new_install:{}:{}'.format(appid, platform), year=now.year, month=now.month):
        mark('request:%s' % appid, userid)
        mark('request:{}:{}'.format(appid, platform), userid)

    mark('request:{}:{}'.format(appid, version), userid)
    mark('request:{}:{}'.format(appid, channel), userid)
    mark('request:{}:{}:{}'.format(appid, platform, version), userid)

def update_live_statistics(userid, apps_list, platform, now=None):
    id = get_id(userid)
    list(map(partial(add_app_live_statistics, id, platform, now=now), apps_list or []))


def add_app_live_statistics(userid, platform, app, now=None):
    mark = partial(mark_event, now=now, track_hourly=True)
    unmark = partial(unmark_event, track_hourly=True)
    appid = app.get('appid')
    version = app.get('version')
    events = app.findall('event')
    nextversion = app.get('nextversion')

    install_event = filter(lambda x: x.get('eventtype') == '2', events)
    if install_event and install_event[0].get('eventresult') == '1':
        mark('online:{}:{}'.format(appid, nextversion), userid)
        mark('online:{}:{}:{}'.format(appid, platform, nextversion), userid)
        return

    update_event = filter(lambda x: x.get('eventtype') == '3', events)
    if update_event and update_event[0].get('eventresult') == '1':
        unmark('online:{}:{}'.format(appid, version), userid)               # necessary for
        unmark('online:{}:{}:{}'.format(appid, platform, version), userid)  # 1 hour interval
        mark('online:{}:{}'.format(appid, nextversion), userid)
        mark('online:{}:{}:{}'.format(appid, platform, nextversion), userid)
        return

    uninstall_event = filter(lambda x: x.get('eventtype') == '4', events)
    if uninstall_event and uninstall_event[0].get('eventresult') == '1':
        unmark('online:{}:{}'.format(appid, version), userid)               # necessary for
        unmark('online:{}:{}:{}'.format(appid, platform, version), userid)  # 1 hour interval
        return

    # updatecheck handling
    if version:
        mark('online:{}:{}'.format(appid, version), userid)
        mark('online:{}:{}:{}'.format(appid, platform, version), userid)

def get_users_statistics_months(app_id, platform=None, year=None, start=1, end=12):
    now = timezone.now()
    if not year:
        year = now.year

    if platform:
        install_event_name = 'new_install:{}:{}'.format(app_id, platform)
        update_event_name = 'request:{}:{}'.format(app_id, platform)
    else:
        install_event_name = 'new_install:%s' % app_id
        update_event_name = 'request:%s' % app_id

    installs_by_month = []
    updates_by_month = []
    for m in range(start, end + 1):
        installs_by_month.append(MonthEvents(install_event_name, year, m))
        updates_by_month.append(MonthEvents(update_event_name, year, m))
    installs_data = [(datetime(year, start + i, 1).strftime("%Y-%m"), len(e)) for i, e in enumerate(installs_by_month)]
    updates_data = [(datetime(year, start + i, 1).strftime("%Y-%m"), len(e)) for i, e in enumerate(updates_by_month)]
    return dict(new=installs_data, updates=updates_data)


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
    if platform == 'win':
        versions = [str(v.version) for v in Version.objects.filter_by_enabled(app__id=app_id)]
    else:
        versions = [str(v.short_version) for v in SparkleVersion.objects.filter_by_enabled(app__id=app_id)]
    event_name = 'request:{}:{}:{}'
    data = [(v, len(MonthEvents(event_name.format(app_id, platform, v), date.year, date.month))) for v in versions]
    return data


def get_users_versions(app_id, date=None):
    if not date:
        date = timezone.now()

    win_data = get_users_versions_by_platform(app_id, 'win', date)
    win_data = filter(lambda x: x[1], win_data)

    mac_data = get_users_versions_by_platform(app_id, 'mac', date)
    mac_data = filter(lambda x: x[1], mac_data)

    data = dict(win=dict(win_data), mac=dict(mac_data))

    return data



def get_versions_data_by_platform(app_id, end, n_hours, versions, platform, tz='UTC'):
    tzinfo = pytz.timezone(tz)
    start = end - timezone.timedelta(hours=n_hours)
    event_name = "online:{}:{}:{}"

    hours = [datetime(start.year, start.month, start.day, start.hour, tzinfo=pytz.UTC)
             + timezone.timedelta(hours=x) for x in range(1, n_hours + 1)]

    data = [(v, [[hour.astimezone(tzinfo).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                  len(HourEvents.from_date(event_name.format(app_id, platform, v), hour))]
                 for hour in hours])
            for v in versions]
    data = filter(lambda version_data: sum([data[1] for data in version_data[1]]), data)
    return dict(data)


def get_users_live_versions(app_id, start, end, tz='UTC'):
    win_versions = [str(v.version) for v in Version.objects.filter_by_enabled(app__id=app_id)]
    mac_versions = [str(v.short_version) for v in SparkleVersion.objects.filter_by_enabled(app__id=app_id)]

    tmp_hours = divmod((end - start).total_seconds(), 60*60)
    n_hours = tmp_hours[0]+1
    n_hours = int(n_hours)

    win_data = get_versions_data_by_platform(app_id, end, n_hours, win_versions, 'win', tz=tz)
    mac_data = get_versions_data_by_platform(app_id, end, n_hours, mac_versions, 'mac', tz=tz)

    data = dict(win=win_data, mac=mac_data)

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
        update_live_statistics(userid, apps, request.os.get('platform'))

    if not filter(lambda app: bool(app.findall('event')), apps):
        return

    req = parse_req(request, ip)
    req.os = parse_os(request.os)
    req.hw = parse_hw(request.hw) if request.get('hw') else None
    req.save()

    parse_apps(apps, req)

