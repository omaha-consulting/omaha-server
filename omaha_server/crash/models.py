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

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from django_extensions.db.models import TimeStampedModel
from raven.contrib.django.raven_compat.models import client
from jsonfield import JSONField
from boto.exception import BotoClientError

from omaha.models import Version
from omaha_server.celery import app


class Crash(TimeStampedModel):
    mini_dump = models.FileField(upload_to='minidump/%Y/%m/%d')
    app_id = models.CharField(max_length=38, null=True, blank=True)
    user_id = models.CharField(max_length=38, null=True, blank=True)
    meta = JSONField(verbose_name='Meta-information', help_text='JSON format', null=True, blank=True)


def symbols_upload_to(obj, filename):
    return os.path.join('symbols', obj.version.app.name, obj.version.channel.name,
                        obj.version.platform.name, filename)


class Symbols(TimeStampedModel):
    version = models.ForeignKey(Version)
    debug_id = models.CharField(verbose_name='Debug ID', max_length=33, db_index=True, null=True, blank=True)
    debug_file = models.CharField(verbose_name='Debug file name', max_length=140, null=True, blank=True)
    file = models.FileField(upload_to=symbols_upload_to)
    is_enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Symbols'

    def _get_head_file(self):
        return self.file.readline().rstrip()

    def _parse_debug_meta_info(self, head):
        head_list = head.split(' ')
        return dict(debug_id=head_list[-2],
                    debug_file=head_list[-1])

    def parse_debug_meta_info(self, save=True):
        head = self._get_head_file()
        debug_meta = self._parse_debug_meta_info(head)
        self.debug_id = debug_meta['debug_id']
        self.debug_file = debug_meta['debug_file']
        if save:
            self.save()


@app.task(ignore_result=True, max_retries=10)
def parse_debug_meta_info(pk):
    try:
        obj = Symbols.objects.get(pk=pk)
        obj.parse_debug_meta_info()
    except BotoClientError:
        client.captureException()
        raise parse_debug_meta_info.retry(countdown=10 * parse_debug_meta_info.request.retries)


@receiver(post_save, sender=Symbols)
def post_symbols_save(sender, instance, created, *args, **kwargs):
    if created:
        parse_debug_meta_info.apply_async(args=(instance.pk,), queue='default')


@receiver(pre_save, sender=Symbols)
def pre_symbols_save(sender, instance, *args, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        if not old.file == instance.file:
            parse_debug_meta_info.apply_async(args=(instance.pk,), queue='default', countdown=3)
