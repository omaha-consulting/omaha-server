# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0004_partialupdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='partialupdate',
            name='active_users',
            field=models.PositiveSmallIntegerField(default=1, help_text=b'Active users in the past ...', choices=[(1, b'week'), (0, b'all'), (2, b'month')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='partialupdate',
            name='exclude_new_users',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
