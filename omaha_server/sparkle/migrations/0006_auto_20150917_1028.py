# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sparkle.models


class Migration(migrations.Migration):

    dependencies = [
        ('sparkle', '0005_auto_20150707_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparkleversion',
            name='file',
            field=models.FileField(null=True, upload_to=sparkle.models.version_upload_to),
        ),
    ]
