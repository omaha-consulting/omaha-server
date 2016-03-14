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

import random
from datetime import datetime
from uuid import uuid4
from optparse import make_option
from multiprocessing import Pool, cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

from django.core.management.base import BaseCommand

from omaha.models import Version, Channel
from omaha.statistics import userid_counting
from sparkle.models import SparkleVersion

NUMBER_UNIQUE = 1000
uuids = dict(
    win=["{%s}" % uuid4() for i in range(NUMBER_UNIQUE)],
    mac=["{%s}" % uuid4() for i in range(NUMBER_UNIQUE)]
)


def get_random_uuid(platform):
    return random.choice(uuids[platform])


def generate_statistics(i, versions, channels, year):
    year = year

    if i % 100 == 0:
        print('=> %s' % i)
    version = random.choice(versions)
    platform = version.platform.name if getattr(version, 'platform', None) else 'mac'
    channel = random.choice(channels)
    if platform == 'win':
        app_list = [dict(
            appid=version.app.id,
            version=str(version.version),
            tag=channel,
        )]
    else:
        app_list = [dict(
            appid=version.app.id,
            version=str(version.short_version),
            tag=version.channel
        )]
    month = random.choice(range(1, 13))
    day = random.choice(range(1, 28))
    date = datetime(year, month, day)
    userid = get_random_uuid(platform)
    userid_counting(userid, app_list, platform, now=date)


def run_worker(data, versions, channels, year):
    t_pool = ThreadPool()
    t_pool.imap_unordered(partial(generate_statistics,
                                  versions=versions,
                                  channels=channels,
                                  year=year), data)
    t_pool.close()
    t_pool.join()


class Command(BaseCommand):
    help = 'A command for generating fake statistics'
    option_list = BaseCommand.option_list + (
        make_option('--count',
                    dest='count',
                    default='1000',
                    type=int,
                    help='Total number of data values (default: 1000)'),
        make_option('--year',
                    dest='year',
                    default=datetime.now().year,
                    type=int,
                    help='Year of statistics (default: Current year)'),
    )

    def handle(self, *args, **options):
        user_count = options['count'] + 1
        year = options['year']
        users = range(1, user_count)
        versions = list(Version.objects.select_related('app', 'platform').filter_by_enabled())
        versions += list(SparkleVersion.objects.select_related('app').filter_by_enabled())
        channels = list(Channel.objects.all())

        job_size = int(user_count / (cpu_count() or 1 * 2)) or 1
        job_data = [users[i:i + job_size] for i in range(0, len(users), job_size)]
        pool = Pool()
        pool.imap_unordered(partial(run_worker, versions=versions, channels=channels, year=year), job_data)
        pool.close()
        pool.join()