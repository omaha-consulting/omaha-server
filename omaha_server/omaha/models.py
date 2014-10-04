# coding: utf8

from django.db import models

from django_extensions.db.models import TimeStampedModel
from versionfield import VersionField


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
    version = VersionField(help_text='Format: 255.255.65535')
    release_notes = models.TextField(blank=True, null=True)
    file = models.FileField()
    file_size = models.PositiveIntegerField()
    file_hash = models.CharField(max_length=140)

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
