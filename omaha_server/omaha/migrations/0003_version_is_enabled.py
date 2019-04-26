# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0002_auto_20141021_0642'),
    ]

    operations = [
        migrations.AddField(
            model_name='version',
            name='is_enabled',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
