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
import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from celery import signature
from django_extensions.db.models import TimeStampedModel
from jsonfield import JSONField

from omaha.models import Version


def crash_upload_to(obj, filename):
    now = timezone.now()
    return os.path.join(*map(str, ['minidump', now.year, now.month,
                                   now.day, uuid.uuid4(), filename]))


def crash_archive_upload_to(obj, filename):
    now = timezone.now()
    return os.path.join(*map(str, ['minidump_archive', now.year, now.month,
                                   now.day, uuid.uuid4(), filename]))


class Crash(TimeStampedModel):
    upload_file_minidump = models.FileField(upload_to=crash_upload_to, blank=True, null=True, max_length=255)
    archive = models.FileField(upload_to=crash_archive_upload_to, blank=True, null=True, max_length=255)
    appid = models.CharField(max_length=38, null=True, blank=True)
    userid = models.CharField(max_length=38, null=True, blank=True)
    meta = JSONField(verbose_name='Meta-information', help_text='JSON format', null=True, blank=True)
    stacktrace = models.TextField(null=True, blank=True)
    stacktrace_json = JSONField(null=True, blank=True)
    signature = models.CharField(max_length=255, db_index=True, null=True, blank=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Crashes'


def symbols_upload_to(obj, filename):
    sym_filename = os.path.splitext(os.path.basename(obj.debug_file))[0]
    sym_filename = '%s.sym' % sym_filename
    return os.path.join('symbols', obj.debug_file, obj.debug_id, sym_filename)


class Symbols(TimeStampedModel):
    debug_id = models.CharField(verbose_name='Debug ID', max_length=255, db_index=True, null=True, blank=True)
    debug_file = models.CharField(verbose_name='Debug file name', max_length=140, null=True, blank=True)
    file = models.FileField(upload_to=symbols_upload_to)

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Symbols'
        unique_together = (
            ('debug_id', 'debug_file'),
        )


@receiver(post_save, sender=Crash)
def crash_post_save(sender, instance, created, *args, **kwargs):
    if created and instance.upload_file_minidump:
        signature("tasks.processing_crash_dump", args=(instance.pk,)).apply_async(queue='default')
