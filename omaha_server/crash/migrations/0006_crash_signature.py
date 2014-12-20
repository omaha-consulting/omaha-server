# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0005_crash_stacktrace_json'),
    ]

    operations = [
        migrations.AddField(
            model_name='crash',
            name='signature',
            field=models.CharField(db_index=True, max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
