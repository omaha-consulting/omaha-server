# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0017_auto_20150616_0853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='userid',
            field=models.CharField(db_index=True, max_length=40, null=True, blank=True),
        ),
    ]
