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
import logging
import uuid

from omaha_server.celery import app
from omaha_server.utils import add_extra_to_log_message, get_splunk_url
from omaha import statistics
from omaha.parser import parse_request
from omaha.limitation import delete_older_than, delete_size_is_exceeded, delete_duplicate_crashes, monitoring_size, raven

logger = logging.getLogger(__name__)

@app.task(ignore_result=True)
def collect_statistics(request, ip=None):
    statistics.collect_statistics(parse_request(request), ip=ip)


@app.task(name='tasks.auto_delete_older_then', ignore_result=True)
def auto_delete_older_than():
    logger = logging.getLogger('limitation')
    model_list = [
        ('crash', 'Crash'),
        ('feedback', 'Feedback')
    ]
    for model in model_list:
        result = delete_older_than(*model)
        if result.get('count', 0):
            result['size'] /= 1024.0 * 1024
            log_id = str(uuid.uuid4())
            params = dict(log_id=log_id)
            splunk_url = get_splunk_url(params)
            splunk_filter = 'log_id=%s' % log_id if splunk_url else None
            raven_extra = dict(id=log_id, splunk_url=splunk_url, splunk_filter=splunk_filter)
            raven.captureMessage("[Limitation]Periodic task 'Older than' cleaned up %d %s, total size of cleaned space is %.2f Mb[%d]" %
                                 (result['count'], model[1], result['size'], time.time()),
                                 data=dict(level=20, logger='limitation'), extra=raven_extra)
            extra = dict(log_id=log_id, meta=True, count=result['count'], size=result['size'], model=model[1], reason='old')
            logger.info(add_extra_to_log_message('Automatic cleanup', extra=extra))
            for element in result['elements']:
                element.update(dict(log_id=log_id))
                logger.info(add_extra_to_log_message('Automatic cleanup element', extra=element))

@app.task(name='tasks.auto_delete_size_is_exceeded', ignore_result=True)
def auto_delete_size_is_exceeded():
    logger = logging.getLogger('limitation')
    model_list = [
        ('crash', 'Crash'),
        ('feedback', 'Feedback')
    ]
    for model in model_list:
        result = delete_size_is_exceeded(*model)
        if result.get('count', 0):
            result['size'] /= 1024.0 * 1024
            log_id = str(uuid.uuid4())
            params = dict(log_id=log_id)
            splunk_url = get_splunk_url(params)
            splunk_filter = 'log_id=%s' % log_id if splunk_url else None
            raven_extra = dict(id=log_id, splunk_url=splunk_url, splunk_filter=splunk_filter)
            raven.captureMessage("[Limitation]Periodic task 'Size is exceeded' cleaned up %d %s, total size of cleaned space is %.2f Mb[%d]" %
                                 (result['count'], model[1], result['size'], time.time()),
                                 data=dict(level=20, logger='limitation'), extra=raven_extra)
            extra = dict(log_id=log_id, meta=True, count=result['count'], size=result['size'], model=model[1], reason='size_is_exceeded')
            logger.info(add_extra_to_log_message('Automatic cleanup', extra=extra))
            for element in result['elements']:
                element.update(dict(log_id=log_id))
                logger.info(add_extra_to_log_message('Automatic cleanup element', extra=element))


@app.task(name='tasks.auto_delete_duplicate_crashes', ignore_result=True)
def auto_delete_duplicate_crashes():
    logger = logging.getLogger('limitation')
    result = delete_duplicate_crashes()
    if result.get('count', 0):
        result['size'] /= 1024.0 * 1024
        log_id = str(uuid.uuid4())
        params = dict(log_id=log_id)
        splunk_url = get_splunk_url(params)
        splunk_filter = 'log_id=%s' % log_id if splunk_url else None
        raven_extra = dict(id=log_id, splunk_url=splunk_url, splunk_filter=splunk_filter)
        raven.captureMessage("[Limitation]Periodic task 'Duplicated' cleaned up %d crashes, total size of cleaned space is %.2f Mb[%d]" %
                             (result['count'], result['size'], time.time()),
                             data=dict(level=20, logger='limitation'), extra=raven_extra)
        extra = dict(log_id=log_id, meta=True, count=result['count'], size=result['size'], reason='duplicated', model='Crash')
        logger.info(add_extra_to_log_message('Automatic cleanup', extra=extra))
        for element in result['elements']:
            element.update(dict(log_id=log_id))
            logger.info(add_extra_to_log_message('Automatic cleanup element', extra=element))

@app.task(name='tasks.deferred_manual_cleanup')
def deferred_manual_cleanup(model, limit_size=None, limit_days=None, limit_duplicated=None):
    logger = logging.getLogger('limitation')
    full_result = dict(count=0, size=0, elements=[])
    if limit_duplicated:
        result = delete_duplicate_crashes(limit=limit_duplicated)
        if result.get('count', 0):
            full_result['count'] += result['count']
            full_result['size'] += result['size']
            full_result['elements'] += result['elements']

    if limit_days:
        result = delete_older_than(*model, limit=limit_days)
        if result.get('count', 0):
            full_result['count'] += result['count']
            full_result['size'] += result['size']
            full_result['elements'] += result['elements']

    if limit_size:
        result = delete_size_is_exceeded(*model, limit=limit_size)
        if result.get('count', 0):
            full_result['count'] += result['count']
            full_result['size'] += result['size']
            full_result['elements'] += result['elements']

    full_result['size'] /= 1024.0 * 1024
    log_id = str(uuid.uuid4())
    params = dict(log_id=log_id)
    splunk_url = get_splunk_url(params)
    splunk_filter = 'log_id=%s' % log_id if splunk_url else None
    raven_extra = dict(id=log_id, splunk_url=splunk_url, splunk_filter=splunk_filter)
    raven.captureMessage("[Limitation]Manual cleanup freed %d %s, total size of cleaned space is %.2f Mb[%s]" %
                         (full_result['count'], model[1], full_result['size'], log_id),
                         data=dict(level=20, logger='limitation'), extra=raven_extra)

    extra = dict(log_id=log_id, meta=True, count=full_result['count'], size=full_result['size'], model=model[1],
                 limit_duplicated=limit_duplicated, limit_size=limit_size, limit_days=limit_days, reason='manual')
    logger.info(add_extra_to_log_message('Manual cleanup', extra=extra))
    for element in full_result['elements']:
        element.update(dict(log_id=log_id))
        logger.info(add_extra_to_log_message('Manual cleanup element', extra=element))


@app.task(name='tasks.auto_monitoring_size', ignore_result=True)
def auto_monitoring_size():
    monitoring_size()
