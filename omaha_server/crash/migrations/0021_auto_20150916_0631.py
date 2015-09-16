# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0020_crash_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crash',
            name='ip',
            field=models.GenericIPAddressField(null=True, protocol=b'ipv4', blank=True),
        ),
    ]
