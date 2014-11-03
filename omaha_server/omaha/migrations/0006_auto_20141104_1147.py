# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import versionfield


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0005_auto_20141030_0606'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('appid', models.CharField(max_length=38, db_index=True)),
                ('version', versionfield.VersionField(default=0, help_text=b'Format: 255.255.65535.65535', null=True, blank=True)),
                ('nextversion', versionfield.VersionField(default=0, help_text=b'Format: 255.255.65535.65535', null=True, blank=True)),
                ('lang', models.CharField(max_length=40, null=True, blank=True)),
                ('tag', models.CharField(max_length=40, null=True, blank=True)),
                ('installage', models.SmallIntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eventtype', models.PositiveSmallIntegerField(db_index=True)),
                ('eventresult', models.PositiveSmallIntegerField()),
                ('errorcode', models.IntegerField(null=True, blank=True)),
                ('extracode1', models.IntegerField(null=True, blank=True)),
                ('download_time_ms', models.PositiveIntegerField(null=True, blank=True)),
                ('downloaded', models.PositiveIntegerField(null=True, blank=True)),
                ('total', models.PositiveIntegerField(null=True, blank=True)),
                ('update_check_time_ms', models.PositiveIntegerField(null=True, blank=True)),
                ('install_time_ms', models.PositiveIntegerField(null=True, blank=True)),
                ('source_url_index', models.URLField(null=True, blank=True)),
                ('state_cancelled', models.PositiveIntegerField(null=True, blank=True)),
                ('time_since_update_available_ms', models.PositiveIntegerField(null=True, blank=True)),
                ('time_since_download_start_ms', models.PositiveIntegerField(null=True, blank=True)),
                ('nextversion', models.CharField(max_length=40, null=True, blank=True)),
                ('previousversion', models.CharField(max_length=40, null=True, blank=True)),
                ('app_request', models.ForeignKey(to='omaha.AppRequest')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Hw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sse', models.PositiveIntegerField(null=True, blank=True)),
                ('sse2', models.PositiveIntegerField(null=True, blank=True)),
                ('sse3', models.PositiveIntegerField(null=True, blank=True)),
                ('ssse3', models.PositiveIntegerField(null=True, blank=True)),
                ('sse41', models.PositiveIntegerField(null=True, blank=True)),
                ('sse42', models.PositiveIntegerField(null=True, blank=True)),
                ('avx', models.PositiveIntegerField(null=True, blank=True)),
                ('physmemory', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Os',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('platform', models.CharField(max_length=10, null=True, blank=True)),
                ('version', models.CharField(max_length=10, null=True, blank=True)),
                ('sp', models.CharField(max_length=40, null=True, blank=True)),
                ('arch', models.CharField(max_length=10, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', versionfield.VersionField(help_text=b'Format: 255.255.65535.65535')),
                ('ismachine', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('sessionid', models.CharField(max_length=40, null=True, blank=True)),
                ('userid', models.CharField(max_length=40, null=True, blank=True)),
                ('installsource', models.CharField(max_length=40, null=True, blank=True)),
                ('originurl', models.URLField(null=True, blank=True)),
                ('testsource', models.CharField(max_length=40, null=True, blank=True)),
                ('updaterchannel', models.CharField(max_length=10, null=True, blank=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, db_index=True, editable=False, blank=True)),
                ('hw', models.ForeignKey(blank=True, to='omaha.Hw', null=True)),
                ('os', models.ForeignKey(blank=True, to='omaha.Os', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='apprequest',
            name='request',
            field=models.ForeignKey(to='omaha.Request'),
            preserve_default=True,
        ),
    ]
