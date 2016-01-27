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
import uuid

from django.core.management.base import BaseCommand
from django.utils import timezone

from freezegun import freeze_time

from omaha.parser import parse_request
from omaha.statistics import collect_statistics
from omaha.models import Version

event_install = b"""<?xml version="1.0" encoding="UTF-8"?>
<request protocol="3.0" version="1.3.23.0" ismachine="1" sessionid="{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}" userid="{%s}" installsource="otherinstallcmd" testsource="ossdev" requestid="{164FC0EC-8EF7-42cb-A49D-474E20E8D352}">
  <os platform="win" version="6.1" sp="" arch="x64"/>
  <app appid="%s" version="" nextversion="%s" lang="en" brand="" client="" installage="6">
    <event eventtype="9" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="5" eventresult="1" errorcode="0" extracode1="0"/>
    <event eventtype="2" eventresult="1" errorcode="0" extracode1="0"/>
  </app>
</request>
"""

def generate_events(app_id, **options):
    versions = Version.objects.filter_by_enabled(app__id=app_id)
    versions = map(lambda x: x.version, versions)

    def generate_fake_hour():
        for version in versions:
            for i in range(random.randint(0, 20)):
                id = uuid.UUID(int=i)
                request = event_install % (id, app_id, version)
                request = bytes(request, 'utf8')
                request = parse_request(request)
                collect_statistics(request)

    start = timezone.now() - timezone.timedelta(days=1)

    for hourdelta in range(1, 25):
        if hourdelta % 10 == 0:
            print('=> ', hourdelta)
        with freeze_time(start + timezone.timedelta(hours=hourdelta)):
            generate_fake_hour()


class Command(BaseCommand):
    args = '<app_id>'
    help = 'A command for generating fake live statistics'

    def handle(self, app_id, *args, **options):
        generate_events(app_id, **options)
