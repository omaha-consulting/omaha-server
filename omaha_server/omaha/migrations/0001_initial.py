# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import versionfield
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
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
                ('version', versionfield.VersionField()),
                ('release_notes', models.TextField(null=True, blank=True)),
                ('file', models.FileField(upload_to=b'')),
                ('file_size', models.PositiveIntegerField()),
                ('file_hash', models.CharField(max_length=140)),
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
    ]
