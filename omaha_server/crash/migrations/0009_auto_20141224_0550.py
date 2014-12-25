# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0008_auto_20141224_0542'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crash',
            old_name='user_id',
            new_name='userid',
        ),
    ]
