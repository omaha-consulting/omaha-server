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
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from celery import signature
from jsonfield import JSONField

from omaha.models import BaseModel
from crash.managers import CrashManager, SymbolsManager


def crash_upload_to(obj, filename):
    now = timezone.now()
    return os.path.join(*map(str, ['minidump', now.year, now.month,
                                   now.day, uuid.uuid4(), filename]))


def crash_archive_upload_to(obj, filename):
    now = timezone.now()
    return os.path.join(*map(str, ['minidump_archive', now.year, now.month,
                                   now.day, uuid.uuid4(), filename]))


class Crash(BaseModel):
    upload_file_minidump = models.FileField(upload_to=crash_upload_to, blank=True, null=True, max_length=255)
    minidump_size = models.PositiveIntegerField(null=True, blank=True)
    archive = models.FileField(upload_to=crash_archive_upload_to, blank=True, null=True, max_length=255)
    archive_size = models.PositiveIntegerField(null=True, blank=True)
    appid = models.CharField(max_length=38, null=True, blank=True)
    userid = models.CharField(max_length=38, null=True, blank=True)
    meta = JSONField(verbose_name='Meta-information', help_text='JSON format', null=True, blank=True)
    stacktrace = models.TextField(null=True, blank=True)
    stacktrace_json = JSONField(null=True, blank=True)
    signature = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    ip = models.GenericIPAddressField(blank=True, null=True, protocol="ipv4")

    objects = CrashManager()

    class Meta(BaseModel.Meta):
        verbose_name_plural = 'Crashes'

    @property
    def size(self):
         return self.archive_size + self.minidump_size

class CrashDescription(BaseModel):
    crash = models.OneToOneField(Crash, related_name='crash_description')
    summary = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)

def symbols_upload_to(obj, filename):
    sym_filename = os.path.splitext(os.path.basename(obj.debug_file))[0]
    sym_filename = '%s.sym' % sym_filename
    return os.path.join('symbols', obj.debug_file, obj.debug_id, sym_filename)


class Symbols(BaseModel):
    debug_id = models.CharField(verbose_name='Debug ID', max_length=255, db_index=True, null=True, blank=True)
    debug_file = models.CharField(verbose_name='Debug file name', max_length=140, null=True, blank=True)
    file = models.FileField(upload_to=symbols_upload_to, null=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)

    objects = SymbolsManager()

    class Meta:
        verbose_name_plural = 'Symbols'
        unique_together = (
            ('debug_id', 'debug_file'),
        )

    @property
    def size(self):
         return self.file_size

@receiver(post_save, sender=Crash)
def crash_post_save(sender, instance, created, *args, **kwargs):
    if created and instance.upload_file_minidump:
        signature("tasks.processing_crash_dump", args=(instance.pk,)).apply_async(queue='private', countdown=1)


@receiver(pre_delete, sender=Crash)
def pre_crash_delete(sender, instance, **kwargs):
    file_fields = [instance.archive, instance.upload_file_minidump]
    for field in file_fields:
        storage, name = field.storage, field.name
        if name:
            storage.delete(name)


@receiver(pre_delete, sender=Symbols)
def pre_symbol_delete(sender, instance, **kwargs):
    storage, name = instance.file.storage, instance.file.name
    if name:
        storage.delete(name)
