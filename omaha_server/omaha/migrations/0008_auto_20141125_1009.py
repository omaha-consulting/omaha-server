# -*- coding: utf-8 -*-


from django.db import models, migrations
import versionfield


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0007_auto_20141113_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='version',
            name='version',
            field=versionfield.VersionField(help_text='Format: 255.255.65535.65535', db_index=True),
            preserve_default=True,
        ),
    ]
