# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import omaha.models


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0020_auto_20150710_0913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='version',
            name='file',
            field=models.FileField(null=True, upload_to=omaha.models._version_upload_to),
        ),
    ]
