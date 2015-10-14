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
import time

from omaha_server.celery import app
from omaha import statistics
from omaha.parser import parse_request
from omaha.limitation import delete_older_than, delete_size_is_exceeded, delete_duplicate_crashes, monitoring_size, raven


@app.task(ignore_result=True)
def collect_statistics(request, ip=None):
    statistics.collect_statistics(parse_request(request), ip=ip)


@app.task(name='tasks.auto_delete_older_then', ignore_result=True)
def auto_delete_older_than():
    model_list = [
        ('crash', 'Crash'),
        ('feedback', 'Feedback')
    ]
    for model in model_list:
        count, size = delete_older_than(*model)
        if count:
            size /= 1024.0 * 1024
            raven.captureMessage("[Limitation]Periodic task 'Older than' cleaned up %d %s, total size of cleaned space is %.2f Mb[%d]" % (count, model[1], size, time.time()),
                                 data={'level': 20, 'logger': 'limitation'})


@app.task(name='tasks.auto_delete_size_is_exceeded', ignore_result=True)
def auto_delete_size_is_exceeded():
    model_list = [
        ('crash', 'Crash'),
        ('feedback', 'Feedback')
    ]
    for model in model_list:
        count, size = delete_size_is_exceeded(*model)
        if count:
            size /= 1024.0 * 1024
            raven.captureMessage("[Limitation]Periodic task 'Size is exceeded' cleaned up %d %s, total size of cleaned space is %.2f Mb[%d]" % (count, model[1], size, time.time()),
                                 data={'level': 20, 'logger': 'limitation'})


@app.task(name='tasks.auto_delete_duplicate_crashes', ignore_result=True)
def auto_delete_duplicate_crashes():
    count, size = delete_duplicate_crashes()
    if count:
        size /= 1024.0 * 1024
        raven.captureMessage("[Limitation]Periodic task 'Duplicated' cleaned up %d crashes, total size of cleaned space is %.2f Mb[%d]" % (count, size, time.time()),
                             data={'level': 20, 'logger': 'limitation'})


@app.task(name='tasks.deferred_manual_cleanup')
def deferred_manual_cleanup(model, limit_size=None, limit_days=None, limit_duplicated=None):
    full_count = 0
    full_size = 0

    if limit_duplicated:
        count, size = delete_duplicate_crashes(limit=limit_duplicated)
        full_count += count
        full_size += size

    if limit_days:
        count, size = delete_older_than(*model, limit=limit_days)
        full_count += count
        full_size += size

    if limit_size:
        count, size = delete_size_is_exceeded(*model, limit=limit_size)
        full_count += count
        full_size += size

    full_size /= 1024.0 * 1024
    raven.captureMessage("[Limitation]Manual cleanup freed %d %s, total size of cleaned space is %.2f Mb[%d]" % (full_count, model[1], full_size, time.time()),
                         data={'level': 20, 'logger': 'limitation'})


@app.task(name='tasks.auto_monitoring_size', ignore_result=True)
def auto_monitoring_size():
    monitoring_size()
