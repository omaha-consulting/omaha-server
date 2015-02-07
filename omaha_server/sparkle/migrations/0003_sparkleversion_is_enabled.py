# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sparkle', '0002_auto_20150112_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='sparkleversion',
            name='is_enabled',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
