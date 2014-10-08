# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import versionfield


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='version',
            name='file_size',
        ),
        migrations.AlterField(
            model_name='version',
            name='version',
            field=versionfield.VersionField(help_text=b'Format: 255.255.65535.65535'),
        ),
    ]
