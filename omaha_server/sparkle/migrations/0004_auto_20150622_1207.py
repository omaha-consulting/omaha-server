# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sparkle', '0003_sparkleversion_is_enabled'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sparkleversion',
            options={'ordering': ['id']},
        ),
    ]
