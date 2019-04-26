# -*- coding: utf-8 -*-

import django.db.models.deletion
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
                ('name', models.PositiveSmallIntegerField(choices=[(1, 'untrusted'), (0, 'install')])),
                ('index', models.CharField(max_length=255)),
                ('value', models.TextField()),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='omaha.Version')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
