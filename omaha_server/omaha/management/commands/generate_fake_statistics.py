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
from uuid import UUID
from optparse import make_option
from multiprocessing import Pool, cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

from django.core.management.base import BaseCommand
from django.utils import timezone

from omaha.models import Version, Channel
from omaha.statistics import userid_counting


def generate_statistics(i, versions, channels):
    now = timezone.now()
    year = now.year

    if i % 100 == 0:
        print('=> %s' % i)
    version = random.choice(versions)
    platform = version.platform.name
    channel = random.choice(channels)
    app_list = [dict(
        appid=version.app.id,
        version=str(version.version),
        tag=channel,
    )]
    month = random.choice(range(1, 13))
    day = random.choice(range(1, 28))
    date = datetime(year, month, day)
    userid = UUID(int=i)
    userid_counting(userid, app_list, platform, now=date)


def run_worker(data, versions, channels):
    t_pool = ThreadPool()
    t_pool.imap_unordered(partial(generate_statistics,
                                  versions=versions,
                                  channels=channels), data)
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
    )

    def handle(self, *args, **options):
        user_count = options['count'] + 1
        users = range(1, user_count)
        versions = list(Version.objects.select_related('app', 'platform').filter_by_enabled())
        channels = list(Channel.objects.all())

        job_size = int(user_count / (cpu_count() or 1 * 2)) or 1
        job_data = [users[i:i + job_size] for i in range(0, len(users), job_size)]

        pool = Pool()
        pool.imap_unordered(partial(run_worker, versions=versions, channels=channels), job_data)
        pool.close()
        pool.join()
