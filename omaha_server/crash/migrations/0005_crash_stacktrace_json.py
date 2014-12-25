# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0004_crash_stacktrace'),
    ]

    operations = [
        migrations.AddField(
            model_name='crash',
            name='stacktrace_json',
            field=jsonfield.fields.JSONField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
