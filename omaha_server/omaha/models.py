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
import hashlib
import base64

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete
from django.utils.timezone import now as datetime_now

from omaha.managers import VersionManager
from omaha.fields import PercentField

from django_extensions.db.fields import (
    CreationDateTimeField, ModificationDateTimeField,
)
from jsonfield import JSONField
from versionfield import VersionField
from furl import furl


__all__ = ['Application', 'Channel', 'Platform', 'Version',
           'Action', 'EVENT_DICT_CHOICES', 'EVENT_CHOICES',
           'Data']

class BaseModel(models.Model):
    created = CreationDateTimeField('created')
    modified = ModificationDateTimeField('modified')

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Application(BaseModel):
    id = models.CharField(max_length=38, primary_key=True)
    name = models.CharField(verbose_name='App', max_length=30, unique=True)

    class Meta:
        db_table = 'applications'
        ordering = ['id']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Platform(BaseModel):
    name = models.CharField(verbose_name='Platform', max_length=10, unique=True, db_index=True)

    class Meta:
        db_table = 'platforms'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Channel(BaseModel):
    name = models.CharField(verbose_name='Channel', max_length=10, unique=True, db_index=True)

    class Meta:
        db_table = 'channels'

    def __str__(self):
        return self.name


def version_upload_to(obj, filename):
    return os.path.join('build', obj.app.name, obj.channel.name,
                        obj.platform.name, str(obj.version), filename)


def _version_upload_to(*args, **kwargs):
    return version_upload_to(*args, **kwargs)


@python_2_unicode_compatible
class Version(BaseModel):
    is_enabled = models.BooleanField(default=True)
    app = models.ForeignKey(Application)
    platform = models.ForeignKey(Platform, db_index=True)
    channel = models.ForeignKey(Channel, db_index=True)
    version = VersionField(help_text='Format: 255.255.65535.65535', number_bits=(8, 8, 16, 16), db_index=True)
    release_notes = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=_version_upload_to, null=True)
    file_hash = models.CharField(verbose_name='Hash', max_length=140, null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)

    objects = VersionManager()

    class Meta:
        db_table = 'versions'
        unique_together = (
            ('app', 'platform', 'channel', 'version'),
        )
        index_together = (
            ('app', 'platform', 'channel', 'version'),
        )
        ordering = ['id']

    def __str__(self):
        return "{app} {version}".format(app=self.app, version=self.version)

    @property
    def file_absolute_url(self):
        url = furl(self.file.url)
        if not url.scheme:
            url = '%s%s' % (settings.OMAHA_URL_PREFIX, url)
        return str(url)

    @property
    def file_package_name(self):
        url = furl(self.file_absolute_url)
        return os.path.basename(url.pathstr)

    @property
    def file_url(self):
        url = furl(self.file_absolute_url)
        return '%s://%s%s/' % (url.scheme, url.host, os.path.dirname(url.pathstr))

    @property
    def size(self):
         return self.file_size

EVENT_DICT_CHOICES = dict(
    preinstall=0,
    install=1,
    postinstall=2,
    update=3,
)

EVENT_CHOICES = zip(EVENT_DICT_CHOICES.values(), EVENT_DICT_CHOICES.keys())


class Action(BaseModel):
    version = models.ForeignKey(Version, db_index=True, related_name='actions')
    event = models.PositiveSmallIntegerField(
        choices=EVENT_CHOICES,
        help_text='Contains a fixed string denoting when this action should be run.')
    run = models.CharField(
        max_length=255, null=True, blank=True,
        help_text='The name of an installer binary to run.')
    arguments = models.CharField(
        max_length=255, null=True, blank=True,
        help_text='Arguments to be passed to that installer binary.')
    successurl = models.URLField(
        null=True, blank=True,
        help_text="A URL to be opened using the system's "
                  "default web browser on a successful install.")
    terminateallbrowsers = models.BooleanField(
        default=False,
        help_text='If "true", close all browser windows before starting the installer binary.')
    successsaction = models.CharField(
        null=True, max_length=255, blank=True,
        help_text='Contains a fixed string denoting some action to take '
                  'in response to a successful install')
    other = JSONField(verbose_name='Other attributes', help_text='JSON format', null=True, blank=True,)

    class Meta:
        db_table = 'actions'
        ordering = ['id']

    def get_attributes(self):
        exclude_fields = ('id', 'version', 'event', 'other', 'created',
                          'modified', 'terminateallbrowsers')
        attrs = dict([(field.name, str(getattr(self, field.name)))
                      for field in self._meta.fields
                      if field.name not in exclude_fields
                      and getattr(self, field.name)])
        if self.terminateallbrowsers:
            attrs['terminateallbrowsers'] = 'true'
        attrs.update(self.other or {})
        return attrs


ACTIVE_USERS_DICT_CHOICES = dict(
    all=0,
    week=1,
    month=2,
)

ACTIVE_USERS_CHOICES = zip(ACTIVE_USERS_DICT_CHOICES.values(), ACTIVE_USERS_DICT_CHOICES.keys())


class PartialUpdate(models.Model):
    is_enabled = models.BooleanField(default=True, db_index=True)
    version = models.OneToOneField(Version, db_index=True)
    percent = PercentField()
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    exclude_new_users = models.BooleanField(default=True)
    active_users = models.PositiveSmallIntegerField(
        help_text='Active users in the past ...',
        choices=ACTIVE_USERS_CHOICES, default=1)


NAME_DATA_DICT_CHOICES = dict(
    install=0,
    untrusted=1,
)

NAME_DATA_CHOICES = zip(NAME_DATA_DICT_CHOICES.values(), NAME_DATA_DICT_CHOICES.keys())


class Data(BaseModel):
    app = models.ForeignKey(Application, db_index=True)
    name = models.PositiveSmallIntegerField(choices=NAME_DATA_CHOICES)
    index = models.CharField(max_length=255, null=True, blank=True)
    value = models.TextField(null=True, blank=True)


class Os(models.Model):
    platform = models.CharField(max_length=10, null=True, blank=True)
    version = models.CharField(max_length=10, null=True, blank=True)
    sp = models.CharField(max_length=40, null=True, blank=True)
    arch = models.CharField(max_length=10, null=True, blank=True)


class Hw(models.Model):
    sse = models.PositiveIntegerField(null=True, blank=True)
    sse2 = models.PositiveIntegerField(null=True, blank=True)
    sse3 = models.PositiveIntegerField(null=True, blank=True)
    ssse3 = models.PositiveIntegerField(null=True, blank=True)
    sse41 = models.PositiveIntegerField(null=True, blank=True)
    sse42 = models.PositiveIntegerField(null=True, blank=True)
    avx = models.PositiveIntegerField(null=True, blank=True)
    physmemory = models.PositiveIntegerField(null=True, blank=True)


class Request(models.Model):
    os = models.ForeignKey(Os, null=True, blank=True)
    hw = models.ForeignKey(Hw, null=True, blank=True)
    version = VersionField(help_text='Format: 255.255.65535.65535', number_bits=(8, 8, 16, 16))
    ismachine = models.PositiveSmallIntegerField(null=True, blank=True)
    sessionid = models.CharField(max_length=40, null=True, blank=True)
    userid = models.CharField(max_length=40, null=True, blank=True)
    installsource = models.CharField(max_length=40, null=True, blank=True)
    originurl = models.URLField(null=True, blank=True)
    testsource = models.CharField(max_length=40, null=True, blank=True)
    updaterchannel = models.CharField(max_length=10, null=True, blank=True)
    created = models.DateTimeField(db_index=True, default=datetime_now, editable=False, blank=True)
    ip = models.GenericIPAddressField(blank=True, null=True)


class Event(models.Model):
    eventtype = models.PositiveSmallIntegerField(db_index=True)
    eventresult = models.PositiveSmallIntegerField()
    errorcode = models.IntegerField(null=True, blank=True)
    extracode1 = models.IntegerField(null=True, blank=True)
    download_time_ms = models.PositiveIntegerField(null=True, blank=True)
    downloaded = models.PositiveIntegerField(null=True, blank=True)
    total = models.PositiveIntegerField(null=True, blank=True)
    update_check_time_ms = models.PositiveIntegerField(null=True, blank=True)
    install_time_ms = models.PositiveIntegerField(null=True, blank=True)
    source_url_index = models.URLField(null=True, blank=True)
    state_cancelled = models.PositiveIntegerField(null=True, blank=True)
    time_since_update_available_ms = models.PositiveIntegerField(null=True, blank=True)
    time_since_download_start_ms = models.PositiveIntegerField(null=True, blank=True)
    nextversion = models.CharField(max_length=40, null=True, blank=True)
    previousversion = models.CharField(max_length=40, null=True, blank=True)

    @property
    def is_error(self):
        if self.eventtype in (100, 102, 103):
            return True
        elif self.eventresult not in (1, 2, 3):
            return True
        elif self.errorcode != 0:
            return True
        return False


class AppRequest(models.Model):
    request = models.ForeignKey(Request, db_index=True)
    appid = models.CharField(max_length=38, db_index=True)
    version = VersionField(help_text='Format: 255.255.65535.65535',
                           number_bits=(8, 8, 16, 16), default=0, null=True, blank=True)
    nextversion = VersionField(help_text='Format: 255.255.65535.65535',
                               number_bits=(8, 8, 16, 16), default=0, null=True, blank=True)
    lang = models.CharField(max_length=40, null=True, blank=True)
    tag = models.CharField(max_length=40, null=True, blank=True)
    installage = models.SmallIntegerField(null=True, blank=True)
    events = models.ManyToManyField(Event)


@receiver(pre_save, sender=Version)
def pre_version_save(sender, instance, *args, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        if old.file == instance.file:
            return
    sha1 = hashlib.sha1()
    for chunk in instance.file.chunks():
        sha1.update(chunk)
    instance.file_hash = base64.b64encode(sha1.digest()).decode()


@receiver(pre_delete, sender=Version)
def pre_version_delete(sender, instance, **kwargs):
    storage, name = instance.file.storage, instance.file.name
    if name:
        storage.delete(name)
