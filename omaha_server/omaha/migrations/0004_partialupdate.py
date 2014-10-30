# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import omaha.fields


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0003_version_is_enabled'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartialUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_enabled', models.BooleanField(default=True)),
                ('percent', omaha.fields.PercentField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('version', models.OneToOneField(to='omaha.Version')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
