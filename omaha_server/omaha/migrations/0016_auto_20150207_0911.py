# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import omaha.models


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0015_remove_version_dsa_signature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='version',
            name='file',
            field=models.FileField(upload_to=omaha.models._version_upload_to),
            preserve_default=True,
        ),
    ]
