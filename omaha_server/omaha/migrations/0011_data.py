# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0010_version_file_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.PositiveSmallIntegerField(choices=[(1, b'untrusted'), (0, b'install')])),
                ('index', models.CharField(max_length=255)),
                ('value', models.TextField()),
                ('version', models.ForeignKey(to='omaha.Version')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
