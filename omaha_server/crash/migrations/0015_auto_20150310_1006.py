# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0014_auto_20150226_0824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crash',
            name='meta',
            field=jsonfield.fields.JSONField(verbose_name='Meta-information', blank=True, null=True, help_text='JSON format'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='symbols',
            name='debug_file',
            field=models.CharField(verbose_name='Debug file name', blank=True, max_length=140, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='symbols',
            name='debug_id',
            field=models.CharField(verbose_name='Debug ID', blank=True, max_length=255, db_index=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='symbols',
            unique_together=set([('debug_id', 'debug_file')]),
        ),
    ]
