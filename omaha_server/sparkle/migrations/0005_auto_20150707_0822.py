# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sparkle', '0004_auto_20150622_1207'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sparkleversion',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='sparkleversion',
            unique_together=set([('app', 'channel', 'version')]),
        ),
    ]
