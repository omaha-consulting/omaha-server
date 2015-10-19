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

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

import os

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete

from omaha.models import BaseModel, Application, Channel
from sparkle.managers import VersionManager


def version_upload_to(obj, filename):
    return os.path.join('sparkle', obj.app.name, obj.channel.name, str(obj.version), filename)


@python_2_unicode_compatible
class SparkleVersion(BaseModel):
    is_enabled = models.BooleanField(default=True)
    app = models.ForeignKey(Application)
    channel = models.ForeignKey(Channel, db_index=True)
    version = models.CharField(max_length=32)
    short_version = models.CharField(max_length=32, blank=True, null=True)
    release_notes = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=version_upload_to, null=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    dsa_signature = models.CharField(verbose_name='DSA signature', max_length=140, null=True, blank=True)

    objects = VersionManager()

    class Meta:
        index_together = (
            ('app', 'channel'),
        )
        unique_together = (
            ('app', 'channel', 'version'),
        )

    def __str__(self):
        return "{app} {version}".format(app=self.app, version=self.version)

    @property
    def file_absolute_url(self):
        return self.file.url

    @property
    def file_package_name(self):
        return os.path.basename(self.file_absolute_url)

    @property
    def file_url(self):
        return '%s/' % os.path.dirname(self.file_absolute_url)

    @property
    def size(self):
        return self.file_size

@receiver(pre_delete, sender=SparkleVersion)
def pre_version_delete(sender, instance, **kwargs):
    storage, name = instance.file.storage, instance.file.name
    if name:
        storage.delete(name)
