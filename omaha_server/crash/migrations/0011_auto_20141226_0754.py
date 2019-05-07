# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0010_crash_archive'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='crash',
            options={'verbose_name_plural': 'Crashes'},
        ),
        migrations.RemoveField(
            model_name='symbols',
            name='version',
        ),
    ]
