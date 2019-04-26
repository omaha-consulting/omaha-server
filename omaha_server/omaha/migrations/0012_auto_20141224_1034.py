# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0011_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='index',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='data',
            name='value',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
