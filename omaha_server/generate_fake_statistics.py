#!/usr/bin/env python
# coding: utf8

import django

django.setup()

import random
from datetime import datetime
from uuid import UUID

from django.utils import timezone

from omaha.models import Version
from omaha.statistics import userid_counting


def generate_statistics(i, versions):
    now = timezone.now()
    year = now.year

    if i % 1000 == 0:
        print '=> %s' % i
    version = random.choice(versions)
    platform = version.platform.name
    app_list = [dict(
        appid=version.app.id,
        version=str(version.version),
    )]
    month = random.choice(range(1, 13))
    day = random.choice(range(1, 28))
    date = datetime(year, month, day)
    userid = UUID(int=i)
    userid_counting(userid, app_list, platform, now=date)


if __name__ == '__main__':
    from multiprocessing import Pool, cpu_count
    from multiprocessing.dummy import Pool as ThreadPool
    from functools import partial

    user_count = 10000
    users = range(1, user_count)
    versions = list(Version.objects.select_related('app', 'platform').filter_by_enabled())

    job_size = user_count / (cpu_count() * 2)
    job_data = [users[i:i + job_size] for i in range(0, len(users), job_size)]

    def run_worker(data, versions):
        t_pool = ThreadPool()
        t_pool.imap_unordered(partial(generate_statistics, versions=versions), data)
        t_pool.close()
        t_pool.join()

    pool = Pool()
    pool.imap_unordered(partial(run_worker, versions=versions), job_data)
    pool.close()
    pool.join()
