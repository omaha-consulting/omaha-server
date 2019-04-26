# -*- coding: utf-8 -*-

import django.db.models.deletion
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
                ('version', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='omaha.Version')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
