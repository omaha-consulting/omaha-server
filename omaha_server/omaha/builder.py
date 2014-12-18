# coding: utf-8

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
from uuid import UUID

from django.utils.timezone import now
from django.db.models import Q

from lxml import etree
from cacheops import cached_as

import tasks
from models import Version
from parser import parse_request
from statistics import is_user_active
from settings import DEFAULT_CHANNEL
from core import (Response, App, Updatecheck_negative, Manifest, Updatecheck_positive,
                  Packages, Package, Actions, Action, Event)


__all__ = ['build_response']


def on_event(event_list, event):
    event_list.append(Event())
    return event_list


def on_action(action_list, action):
    action = Action(
        event=action.get_event_display(),
        **action.get_attributes()
    )
    action_list.append(action)
    return action_list


def is_new_user(version):
    if version == '':
        return True
    return False


@cached_as(Version, timeout=60)
def _get_version(partialupdate, app_id, platform, channel, version, date=None):
    date = date or now()

    version_qs = Version.objects.filter_by_enabled(
        app=app_id,
        platform__name=platform,
        channel__name=channel)
    if version:
        version_qs = version_qs.filter(version__gt=version)
    version_qs = version_qs.prefetch_related("actions", "partialupdate")

    if partialupdate:
        try:
            new_version = version_qs.filter(partialupdate__is_enabled=True,
                                            partialupdate__start_date__lte=date,
                                            partialupdate__end_date__gte=date).cache().latest('version')
        except Version.DoesNotExist:
            return None
    else:
        new_version = version_qs.filter(
            Q(partialupdate__isnull=True)
            | Q(partialupdate__is_enabled=False)).cache().latest('version')

    return new_version


def get_version(app_id, platform, channel, version, userid, date=None):
    try:
        new_version = _get_version(True, app_id, platform, channel, version, date=date)

        if not new_version:
            raise Version.DoesNotExist

        if new_version.partialupdate.exclude_new_users and is_new_user(version):
            raise Version.DoesNotExist

        if not is_user_active(new_version.partialupdate.active_users, userid):
            raise Version.DoesNotExist

        userid_int = UUID(userid).int
        percent = new_version.partialupdate.percent
        if not (userid_int % int(100 / percent)) == 0:
            raise Version.DoesNotExist
    except Version.DoesNotExist:
        new_version = _get_version(False, app_id, platform, channel, version, date=date)

    return new_version


def on_app(apps_list, app, os, userid):
    app_id = app.get('appid')
    version = app.get('version')
    platform = os.get('platform')
    channel = app.get('tag') or DEFAULT_CHANNEL
    ping = bool(app.findall('ping'))
    events = reduce(on_event, app.findall('event'), [])
    AppPartial = partial(App, app_id, status='ok', ping=ping, events=events)

    if app.findall('updatecheck'):
        try:
            version = get_version(app_id, platform, channel, version, userid)
            actions = reduce(on_action, version.actions.all(), [])
            updatecheck = Updatecheck_positive(
                urls=[version.file_url],
                manifest=Manifest(
                    version=str(version.version),
                    packages=Packages([Package(
                        name=version.file_package_name,
                        required='true',
                        size=str(version.file_size),
                        hash=version.file_hash,
                    )]),
                    actions=Actions(actions),
                )
            )
            apps_list.append(AppPartial(updatecheck=updatecheck))
        except Version.DoesNotExist:
            apps_list.append(AppPartial(updatecheck=Updatecheck_negative()))
    else:
        apps_list.append(AppPartial())

    return apps_list


def build_response(request, pretty_print=True):
    obj = parse_request(request)
    tasks.collect_statistics.apply_async(args=(request,), queue='transient')
    userid = obj.get('userid')
    apps = obj.findall('app')
    apps_list = reduce(partial(on_app, os=obj.os, userid=userid), apps, [])
    response = Response(apps_list, date=now())
    return etree.tostring(response, pretty_print=pretty_print,
                          xml_declaration=True, encoding='UTF-8')
