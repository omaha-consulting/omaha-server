# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0008_auto_20141125_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partialupdate',
            name='end_date',
            field=models.DateField(db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='partialupdate',
            name='is_enabled',
            field=models.BooleanField(default=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='partialupdate',
            name='start_date',
            field=models.DateField(db_index=True),
            preserve_default=True,
        ),
    ]
