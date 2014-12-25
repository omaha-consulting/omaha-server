# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import crash.models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0009_auto_20141125_1013'),
        ('crash', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Symbols',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('debug_id', models.CharField(db_index=True, max_length=33, null=True, verbose_name=b'Debug ID', blank=True)),
                ('debug_file', models.CharField(max_length=140, null=True, verbose_name=b'Debug file name', blank=True)),
                ('file', models.FileField(upload_to=crash.models.symbols_upload_to)),
                ('is_enabled', models.BooleanField(default=False)),
                ('version', models.ForeignKey(to='omaha.Version')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
    ]
