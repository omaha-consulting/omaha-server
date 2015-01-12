# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields
import sparkle.models


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0014_auto_20150112_1025'),
    ]

    operations = [
        migrations.CreateModel(
            name='SparkleVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('version', models.CharField(max_length=32)),
                ('short_version', models.CharField(max_length=32, null=True, blank=True)),
                ('release_notes', models.TextField(null=True, blank=True)),
                ('file', models.FileField(upload_to=sparkle.models.version_upload_to)),
                ('file_size', models.PositiveIntegerField(null=True, blank=True)),
                ('dsa_signature', models.CharField(max_length=140, verbose_name=b'DSA signature')),
                ('app', models.ForeignKey(to='omaha.Application')),
                ('channel', models.ForeignKey(to='omaha.Channel')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='sparkleversion',
            index_together=set([('app', 'channel')]),
        ),
    ]
