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

from __future__ import print_function
from builtins import range, bytes

import random
from datetime import datetime
from uuid import uuid4
from optparse import make_option

from django.core.management.base import BaseCommand

from freezegun import freeze_time

from omaha.parser import parse_request
from omaha.statistics import collect_statistics
from omaha.models import Version


os_version_list = [
    '5.0',
    '5.1',
    '5.2',
    '6.0',
    '6.1',
    '6.2',
    '6.3']

os_sp_list = [
    'Service Pack 1',
    'Service Pack 2',
    'Service Pack 3']

os_arch_list = ['x86', 'x64']

request_tml = """<?xml version="1.0" encoding="UTF-8"?>
<request protocol="3.0" version="1.3.23.0" ismachine="0" sessionid="{sessionid}" installsource="taggedmi" testsource="auto" requestid="{requestid}"
userid="{userid}" >
<os platform="win" version="{os_version}" sp="{os_sp}" arch="{os_arch}"/>
<app appid="{app_id}" version="{version}" nextversion="{nextversion}" lang="en" brand="" client="" installage="-1">
  {events}
</app>
</request>"""

event_list = [
    """<event eventtype="9" eventresult="1" errorcode="0" extracode1="0"/>
  <event eventtype="5" eventresult="1" errorcode="0" extracode1="0"/>
  <event eventtype="1" eventresult="1" errorcode="0" extracode1="0" download_time_ms="3903" downloaded="32768" total="32768"/>
  <event eventtype="6" eventresult="1" errorcode="0" extracode1="0"/>
  <event eventtype="2" eventresult="5" errorcode="1639" extracode1="0"/>""",
    """<event eventtype="9" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="5" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="1" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="6" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="2" eventresult="0" errorcode="-2147219195" extracode1="268435469"/>""",
    """<event eventtype="9" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="5" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="1" eventresult="1" errorcode="0" extracode1="0" download_time_ms="3903" downloaded="32768" total="32768"/>
    <event eventtype="6" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="2" eventresult="5" errorcode="1639" extracode1="0"/>""",
]


def get_random_uuid():
    return "{%s}" % uuid4()


def get_random_date():
    month = random.choice(range(1, 13))
    day = random.choice(range(1, 28))
    return datetime(2014, month, day)


def generate_events(app_id, **options):
    versions = Version.objects.filter_by_enabled(app__id=app_id)

    userid_list = list(map(lambda x: get_random_uuid(), range(1, 25)))
    sessionid_list = list(map(lambda x: get_random_uuid(), range(1, 50)))

    for i in range(1, options['count'] + 1):
        if i % 10 == 0:
            print('=> ', i)

        version = random.choice(versions)
        request = request_tml.format(
            sessionid=random.choice(sessionid_list),
            requestid=get_random_uuid(),
            userid=random.choice(userid_list),
            os_version=random.choice(os_version_list),
            os_sp=random.choice(os_sp_list),
            os_arch=random.choice(os_arch_list),
            app_id=app_id,
            version=str(version.version),
            nextversion='',
            events=random.choice(event_list)
        )

        request = bytes(request, 'utf8')

        request_obj = parse_request(request)

        with freeze_time(get_random_date()):
            collect_statistics(request_obj, ip='8.8.8.8')


class Command(BaseCommand):
    args = '<app_id>'
    help = 'A command for generating fake data such as requests, events and statistics'
    option_list = BaseCommand.option_list + (
        make_option('--count',
                    dest='count',
                    default='100',
                    type=int,
                    help='Total number of data values (default: 100)'),
    )

    def handle(self, app_id, *args, **options):
        generate_events(app_id, **options)
