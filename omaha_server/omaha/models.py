# coding: utf8

import os
import hashlib
import base64

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save

from django_extensions.db.models import TimeStampedModel
from versionfield import VersionField


__all__ = ['Application', 'Channel', 'Platform', 'Version']


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


class Version(TimeStampedModel):
    app = models.ForeignKey(Application)
    platform = models.ForeignKey(Platform)
    channel = models.ForeignKey(Channel)
    version = VersionField(help_text='Format: 255.255.65535.65535', number_bits=(8, 8, 16, 16))
    release_notes = models.TextField(blank=True, null=True)
    file = models.FileField()
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
