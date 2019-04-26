# -*- coding: utf-8 -*-

import django.db.models.deletion
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0013_data_app'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='app',
            field=models.ForeignKey(to='omaha.Application', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
