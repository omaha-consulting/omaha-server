# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_grant_permissions_to_public_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 9, 7, 54, 53, 904652, tzinfo=utc), auto_now_add=True, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedback',
            name='ip',
            field=models.IPAddressField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 9, 7, 55, 2, 994579, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
