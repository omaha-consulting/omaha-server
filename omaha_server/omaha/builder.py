# coding: utf-8

from functools import partial

from django.utils.timezone import now

from lxml import etree

from models import Version
from parser import parse_request
from core import (Response, App, Updatecheck_negative, Manifest, Updatecheck_positive,
                  Packages, Package, Actions, Action)


__all__ = ['build_response']


def on_app(apps_list, app, os, channel):
    app_id = app.get('appid')
    version = app.get('version')
    platform = os.get('platform')
    ping = bool(app.findall('ping'))
    app = partial(App, app_id, status='ok', ping=ping)

    try:
        version = Version.objects.filter(app=app_id,
                                         platform__name=platform,
                                         channel__name=channel,
                                         version__gt=version).latest('version')
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
                actions=Actions([
                    Action(event='install', arguments='--do-not-launch-chrome',
                           run='chrome_installer.exe'),
                    Action(event='postinstall', version=str(version.version),
                           onsuccess='exitsilentlyonlaunchcmd'),
                ])
            )
        )
        apps_list.append(app(updatecheck=updatecheck))
    except Version.DoesNotExist:
        apps_list.append(app(updatecheck=Updatecheck_negative()))

    return apps_list


def build_response(request, pretty_print=True):
    obj = parse_request(request)
    channel = obj.get('updaterchannel', 'stable')
    apps_list = reduce(partial(on_app, os=obj.os, channel=channel), obj.findall('app'), [])
    response = Response(apps_list, date=now())
    return etree.tostring(response, pretty_print=pretty_print,
                          xml_declaration=True, encoding='UTF-8')
