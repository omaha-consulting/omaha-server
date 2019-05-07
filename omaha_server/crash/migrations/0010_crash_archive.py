# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0009_auto_20141224_0550'),
    ]

    operations = [
        migrations.AddField(
            model_name='crash',
            name='archive',
            field=models.FileField(null=True, upload_to='minidump_archive/%Y/%m/%d', blank=True),
            preserve_default=True,
        ),
    ]
