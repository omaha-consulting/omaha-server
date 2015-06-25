# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0016_auto_20150622_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrashDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('summary', models.CharField(max_length=500)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='crashdescription',
            name='crash',
            field=models.OneToOneField(related_name='crash_description', to='crash.Crash'),
        ),
    ]
