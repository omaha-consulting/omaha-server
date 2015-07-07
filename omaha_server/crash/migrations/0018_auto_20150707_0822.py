# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0017_auto_20150625_1042'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='crash',
            options={'verbose_name_plural': 'Crashes'},
        ),
        migrations.AlterModelOptions(
            name='crashdescription',
            options={},
        ),
        migrations.AlterModelOptions(
            name='symbols',
            options={'verbose_name_plural': 'Symbols'},
        ),
    ]
