# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0015_auto_20150310_1006'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='crash',
            options={'ordering': ['id'], 'verbose_name_plural': 'Crashes'},
        ),
        migrations.AlterModelOptions(
            name='symbols',
            options={'ordering': ['id'], 'verbose_name_plural': 'Symbols'},
        ),
    ]
