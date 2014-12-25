# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_app(apps, schema_editor):
    Data = apps.get_model("omaha", "Data")

    for data in Data.objects.select_related('version').all():
        data.app = data.version.app
        data.save()


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0012_auto_20141224_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='app',
            field=models.ForeignKey(to='omaha.Application', null=True),
            preserve_default=True,
        ),
        migrations.RunPython(set_app),
        migrations.RemoveField('data', 'version'),
    ]
