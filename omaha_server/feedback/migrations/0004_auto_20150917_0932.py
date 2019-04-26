# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0003_auto_20150909_0755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='ip',
            field=models.GenericIPAddressField(null=True, blank=True),
        ),
    ]
