# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0007_auto_20141223_0911'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crash',
            old_name='app_id',
            new_name='appid',
        ),
    ]
