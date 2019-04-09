# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0014_auto_20150112_1025'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='version',
            name='dsa_signature',
        ),
    ]
