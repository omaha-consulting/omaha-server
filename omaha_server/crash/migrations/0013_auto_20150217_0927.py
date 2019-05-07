# -*- coding: utf-8 -*-


from django.db import models, migrations
import crash.models


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0012_auto_20150203_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crash',
            name='upload_file_minidump',
            field=models.FileField(max_length=255, null=True, upload_to=crash.models.crash_upload_to, blank=True),
            preserve_default=True,
        ),
    ]
