# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0013_auto_20150217_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='symbols',
            name='debug_id',
            field=models.CharField(db_index=True, max_length=255, null=True, verbose_name='Debug ID', blank=True),
            preserve_default=True,
        ),
    ]
