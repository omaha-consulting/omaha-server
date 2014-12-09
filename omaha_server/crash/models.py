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

from django_extensions.db.models import TimeStampedModel
from jsonfield import JSONField

from omaha.models import Version


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

    class Meta:
        verbose_name_plural = 'Symbols'
