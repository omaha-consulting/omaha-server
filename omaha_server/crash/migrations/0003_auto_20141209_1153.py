# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0002_symbols'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='symbols',
            options={'verbose_name_plural': 'Symbols'},
        ),
        migrations.RemoveField(
            model_name='symbols',
            name='is_enabled',
        ),
    ]
