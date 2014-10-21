# coding: utf-8

from functools import partial

from django.utils.timezone import now

from lxml import etree
from raven.contrib.django.raven_compat.models import client

from models import Version
from parser import parse_request
from statistics import userid_counting
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


def on_app(apps_list, app, os, channel):
    app_id = app.get('appid')
    version = app.get('version')
    platform = os.get('platform')
    ping = bool(app.findall('ping'))
    events = reduce(on_event, app.findall('event'), [])
    AppPartial = partial(App, app_id, status='ok', ping=ping, events=events)

    if app.findall('updatecheck'):
        try:
            version_qs = Version.objects.filter(app=app_id,
                                                platform__name=platform,
                                                channel__name=channel)
            if version:
                version_qs = version_qs.filter(version__gt=version)
            version_qs = version_qs.prefetch_related("actions")
            version = version_qs.latest('version')
            actions = reduce(on_action, version.actions.all(), [])
            updatecheck = Updatecheck_positive(
                urls=[version.file_url],
                manifest=Manifest(
                    version=str(version.version),
                    packages=Packages([Package(
                        name=version.file_package_name,
                        required='true',
                        size=str(version.file.size),
                        hash=version.file_hash,
                    )]),
                    actions=Actions(actions),
                )
            )
            apps_list.append(AppPartial(updatecheck=updatecheck))
        except Version.DoesNotExist:
            client.captureException()
            apps_list.append(AppPartial(updatecheck=Updatecheck_negative()))
    else:
        apps_list.append(AppPartial())

    return apps_list


def build_response(request, pretty_print=True):
    obj = parse_request(request)
    channel = obj.get('updaterchannel', 'stable')
    userid = obj.get('userid')
    apps_list = reduce(partial(on_app, os=obj.os, channel=channel), obj.findall('app'), [])
    if userid:
        userid_counting(userid, map(lambda i: i.get('appid'), apps_list))
    response = Response(apps_list, date=now())
    return etree.tostring(response, pretty_print=pretty_print,
                          xml_declaration=True, encoding='UTF-8')
