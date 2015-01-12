# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0013_data_app'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='app',
            field=models.ForeignKey(to='omaha.Application'),
            preserve_default=True,
        ),
    ]
