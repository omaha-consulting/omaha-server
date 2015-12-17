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

import os
import logging

from django.conf import settings

from furl import furl
from clom.shell import CommandError
import requests

from omaha_server.celery import app
from crash.models import Crash
from crash.settings import S3_MOUNT_PATH
from crash.utils import (
    get_stacktrace,
    FileNotFoundError,
    parse_stacktrace,
    get_signature,
    send_stacktrace_sentry,
)


logger = logging.getLogger(__name__)
SENTRY_DOMAIN = getattr(settings, 'SENTRY_STACKTRACE_DOMAIN', None)
SENTRY_ORG_SLUG = getattr(settings, 'SENTRY_STACKTRACE_ORG_SLUG', None)
SENTRY_PROJ_SLUG = getattr(settings, 'SENTRY_STACKTRACE_PROJ_SLUG', None)
SENTRY_API_KEY = getattr(settings, 'SENTRY_STACKTRACE_API_KEY', None)

@app.task(name='tasks.processing_crash_dump', ignore_result=True, max_retries=12, bind=True)
def processing_crash_dump(self, crash_pk):
    try:
        crash = Crash.objects.get(pk=crash_pk)
        url = furl(crash.upload_file_minidump.url)
        path = url.pathstr
        crash_dump_path = os.path.join(S3_MOUNT_PATH, *path.split('/'))
        stacktrace, errors = get_stacktrace(crash_dump_path)
        crash.stacktrace = stacktrace
        crash.stacktrace_json = parse_stacktrace(stacktrace)
        crash.signature = get_signature(crash.stacktrace_json)
        crash.save()
        send_stacktrace_sentry(crash)
    except FileNotFoundError as exc:
        logger.error('Failed processing_crash_dump',
                     exc_info=True,
                     extra=dict(crash_pk=crash_pk,
                                crash_dump_path=crash_dump_path))
        raise self.retry(exc=exc, countdown=2 ** processing_crash_dump.request.retries)
    except CommandError as exc:
        logger.error('Failed processing_crash_dump',
                     exc_info=True,
                     extra=dict(crash_pk=crash_pk,
                                crash_dump_path=crash_dump_path))
        raise exc


@app.task(name='tasks.get_sentry_link', ignore_result=True, max_retries=6, bind=True)
def get_sentry_link(self, crash_pk, event_id):
    try:
        if SENTRY_DOMAIN and SENTRY_ORG_SLUG and SENTRY_PROJ_SLUG and SENTRY_API_KEY:
            crash = Crash.objects.get(pk=crash_pk)
            resp = requests.get(
                'http://%s/api/0/projects/%s/%s/events/%s/' % (SENTRY_DOMAIN, SENTRY_ORG_SLUG, SENTRY_PROJ_SLUG, event_id,),
                auth=(SENTRY_API_KEY, '')
            ).json()

            crash.groupid = resp['groupID']
            crash.eventid = resp['id']
            crash.save()
        else:
            logging.warning("Sentry is not congured")
    except KeyError as exc:
        logging.error("Sentry event not found")
        raise self.retry(exc=exc, countdown=2 ** get_sentry_link.request.retries)
