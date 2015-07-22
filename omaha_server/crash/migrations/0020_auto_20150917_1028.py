# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import crash.models


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0019_auto_20150722_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='symbols',
            name='file',
            field=models.FileField(null=True, upload_to=crash.models.symbols_upload_to),
        ),
    ]
