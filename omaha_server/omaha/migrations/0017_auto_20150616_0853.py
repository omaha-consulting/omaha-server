# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0016_auto_20150207_0911'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='action',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='application',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='channel',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='platform',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='version',
            options={'ordering': ['id']},
        ),
    ]
