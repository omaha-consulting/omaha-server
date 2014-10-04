# coding: utf-8

from django.utils.timezone import now

from lxml import etree

from models import Application
from parser import parse_request
from core import Response, App, Updatecheck_negative


__all__ = ['build_response']


def on_app(apps_list, app):
    app_id = app.get('appid')
    try:
        application = Application.objects.get(id=app_id)
    except Application.DoesNotExist:
        apps_list.append(App(
            app_id=app_id,
            updatecheck=Updatecheck_negative(),
            ping=bool(len(app.find('ping')))
        ))
    return apps_list


def build_response(request, pretty_print=True):
    obj = parse_request(request)
    apps_list = reduce(on_app, obj.find('app'), [])
    response = Response(apps_list, date=now())
    return etree.tostring(response, pretty_print=pretty_print, xml_declaration=True, encoding='UTF-8')