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


from builtins import range, bytes

import random
import uuid
from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils import timezone

from freezegun import freeze_time

from omaha.parser import parse_request
from omaha.statistics import collect_statistics
from omaha.models import Version

event_updatecheck = b"""<?xml version="1.0" encoding="UTF-8"?>
<request protocol="3.0"
         version="1.3.23.0"
         ismachine="0"
         sessionid="{5FAD27D4-6BFA-4daa-A1B3-5A1F821FEE0F}"
         userid="{%s}"
         installsource="scheduler"
         testsource="ossdev"
         requestid="{C8F6EDF3-B623-4ee6-B2DA-1D08A0B4C665}">
    <os platform="win" version="6.1" sp="" arch="x64"/>
    <app appid="%s" version="%s" nextversion="" lang="en" brand="GGLS"
         client="someclientid" installage="39" tag="%s">
        <updatecheck/>
        <ping r="1"/>
    </app>
</request>"""

def generate_events(app_id, **options):
    versions = Version.objects.filter_by_enabled(app__id=app_id)
    n_hours = options['n_hours']

    def generate_fake_hour():
        for version in versions:
            for i in range(random.randint(0, 20)):
                id = uuid.UUID(int=i)
                request = event_updatecheck % (id, app_id, version.version, version.channel)
                request = bytes(request, 'utf8')
                request = parse_request(request)
                collect_statistics(request)

    start = timezone.now() - timezone.timedelta(hours=n_hours)

    for hourdelta in range(0, n_hours + 1):
        if hourdelta % 10 == 0:
            print('=> ', hourdelta)
        with freeze_time(start + timezone.timedelta(hours=hourdelta)):
            generate_fake_hour()


class Command(BaseCommand):
    args = '<app_id>'
    help = 'A command for generating fake live statistics'

    def handle(self, app_id, *args, **options):
        generate_events(app_id, **options)

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            dest='n_hours',
            default='24',
            type=int,
            help='For how many hours will be generated fake data(default: 24)'
        )
