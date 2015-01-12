# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sparkle', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparkleversion',
            name='dsa_signature',
            field=models.CharField(max_length=140, null=True, verbose_name=b'DSA signature', blank=True),
            preserve_default=True,
        ),
    ]
