# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0002_auto_20141008_0708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='version',
            name='file_hash',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
    ]
