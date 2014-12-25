# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0003_auto_20141209_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='crash',
            name='stacktrace',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
