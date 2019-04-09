# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0023_auto_20151209_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='crash',
            name='eventid',
            field=models.CharField(max_length=38, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='crash',
            name='groupid',
            field=models.CharField(max_length=38, null=True, blank=True),
        ),
    ]
