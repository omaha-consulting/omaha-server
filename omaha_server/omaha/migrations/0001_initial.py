# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import versionfield
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('event', models.PositiveSmallIntegerField(help_text=b'Contains a fixed string denoting when this action should be run.', choices=[(2, b'postinstall'), (1, b'install'), (3, b'update'), (0, b'preinstall')])),
                ('run', models.CharField(help_text=b'The name of an installer binary to run.', max_length=255, null=True, blank=True)),
                ('arguments', models.CharField(help_text=b'Arguments to be passed to that installer binary.', max_length=255, null=True, blank=True)),
                ('successurl', models.URLField(help_text=b"A URL to be opened using the system's default web browser on a successful install.", null=True, blank=True)),
                ('terminateallbrowsers', models.BooleanField(default=False, help_text=b'If "true", close all browser windows before starting the installer binary.')),
                ('successsaction', models.CharField(help_text=b'Contains a fixed string denoting some action to take in response to a successful install', max_length=255, null=True, blank=True)),
                ('other', jsonfield.fields.JSONField(help_text=b'JSON format', null=True, verbose_name=b'Other attributes', blank=True)),
            ],
            options={
                'db_table': 'actions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('id', models.CharField(max_length=38, serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30, verbose_name=b'App')),
            ],
            options={
                'db_table': 'applications',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('name', models.CharField(unique=True, max_length=10, verbose_name=b'Channel', db_index=True)),
            ],
            options={
                'db_table': 'channels',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('name', models.CharField(unique=True, max_length=10, verbose_name=b'Platform', db_index=True)),
            ],
            options={
                'db_table': 'platforms',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('version', versionfield.VersionField(help_text=b'Format: 255.255.65535.65535')),
                ('release_notes', models.TextField(null=True, blank=True)),
                ('file', models.FileField(upload_to=b'')),
                ('file_hash', models.CharField(max_length=140, null=True, verbose_name=b'Hash', blank=True)),
                ('app', models.ForeignKey(to='omaha.Application')),
                ('channel', models.ForeignKey(to='omaha.Channel')),
                ('platform', models.ForeignKey(to='omaha.Platform')),
            ],
            options={
                'db_table': 'versions',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='version',
            unique_together=set([('app', 'platform', 'channel', 'version')]),
        ),
        migrations.AlterIndexTogether(
            name='version',
            index_together=set([('app', 'platform', 'channel', 'version')]),
        ),
        migrations.AddField(
            model_name='action',
            name='version',
            field=models.ForeignKey(related_name=b'actions', to='omaha.Version'),
            preserve_default=True,
        ),
    ]
