# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0006_crash_signature'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crash',
            old_name='mini_dump',
            new_name='upload_file_minidump',
        ),
    ]
