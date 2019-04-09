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

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.test import RequestFactory

from freezegun import freeze_time

from sparkle.statistics import collect_statistics
from sparkle.models import SparkleVersion
from omaha.models import Application

def generate_events(app_name,  **options):
    app_id = Application.objects.get(name=app_name).id
    versions = SparkleVersion.objects.filter_by_enabled(app__name=app_name)
    request_factory = RequestFactory()

    def generate_fake_hour():
        for version in versions:
            for i in range(random.randint(0, 20)):
                id = uuid.UUID(int=i)
                request = request_factory.get('/sparkle/%s/%s/appcast.xml?appVersionShort=%s&deviceID=%s' % (
                    app_name,
                    version.channel,
                    version.short_version,
                    id
                ))
                collect_statistics(request, app_id, version.channel)

    start = timezone.now() - timezone.timedelta(days=1)

    for hourdelta in range(1, 25):
        if hourdelta % 10 == 0:
            print('=> ', hourdelta)
        with freeze_time(start + timezone.timedelta(hours=hourdelta)):
            generate_fake_hour()


class Command(BaseCommand):
    args = '<app_name>'
    help = 'A command for generating fake live statistics'

    def handle(self, app_name, *args, **options):
        generate_events(app_name, **options)
