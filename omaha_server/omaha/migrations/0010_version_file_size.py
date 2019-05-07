# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0009_auto_20141125_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='version',
            name='file_size',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
