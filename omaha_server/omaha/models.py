# coding: utf8

import os
import hashlib
import base64

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save

from django_extensions.db.models import TimeStampedModel
from jsonfield import JSONField
from versionfield import VersionField


__all__ = ['Application', 'Channel', 'Platform', 'Version',
           'Action', 'EVENT_DICT_CHOICES', 'EVENT_CHOICES']


class Application(TimeStampedModel):
    id = models.CharField(max_length=38, primary_key=True)
    name = models.CharField(verbose_name='App', max_length=30, unique=True)

    class Meta:
        db_table = 'applications'

    def __unicode__(self):
        return self.name


class Platform(TimeStampedModel):
    name = models.CharField(verbose_name='Platform', max_length=10, unique=True, db_index=True)

    class Meta:
        db_table = 'platforms'

    def __unicode__(self):
        return self.name


class Channel(TimeStampedModel):
    name = models.CharField(verbose_name='Channel', max_length=10, unique=True, db_index=True)

    class Meta:
        db_table = 'channels'

    def __unicode__(self):
        return self.name


def version_upload_to(obj, filename):
    return os.path.join('build', obj.app.name, obj.channel.name,
                        obj.platform.name, filename)


class Version(TimeStampedModel):
    app = models.ForeignKey(Application)
    platform = models.ForeignKey(Platform)
    channel = models.ForeignKey(Channel)
    version = VersionField(help_text='Format: 255.255.65535.65535', number_bits=(8, 8, 16, 16))
    release_notes = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=lambda o, f: version_upload_to(o, f))
    file_hash = models.CharField(verbose_name='Hash', max_length=140, null=True, blank=True)

    class Meta:
        db_table = 'versions'
        unique_together = (
            ('app', 'platform', 'channel', 'version'),
        )
        index_together = (
            ('app', 'platform', 'channel', 'version'),
        )

    def __unicode__(self):
        return u"{app} {version}".format(app=self.app, version=self.version)

    @property
    def file_absolute_url(self):
        return self.file.url

    @property
    def file_package_name(self):
        return os.path.basename(self.file_absolute_url)

    @property
    def file_url(self):
        return '%s/' % os.path.dirname(self.file_absolute_url)


EVENT_DICT_CHOICES = dict(
    preinstall=0,
    install=1,
    postinstall=2,
    update=3,
)

EVENT_CHOICES = zip(EVENT_DICT_CHOICES.values(), EVENT_DICT_CHOICES.keys())


class Action(TimeStampedModel):
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

    def get_attributes(self):
        exclude_fields = ('id', 'version', 'event', 'other', 'created', 'modified')
        attrs = dict([(field.name, str(getattr(self, field.name)).lower())
                      for field in self._meta.fields
                      if field.name not in exclude_fields
                      and getattr(self, field.name)])
        attrs.update(self.other or {})
        return attrs



@receiver(pre_save, sender=Version)
def pre_version_save(sender, instance, *args, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        if old.file == instance.file:
            return
    sha1 = hashlib.sha1()
    for chunk in instance.file.chunks():
        sha1.update(chunk)
    instance.file_hash = base64.b64encode(sha1.digest())
