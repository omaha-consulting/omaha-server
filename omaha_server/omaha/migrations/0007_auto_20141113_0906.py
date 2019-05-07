# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0006_auto_20141104_1147'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='app_request',
        ),
        migrations.AddField(
            model_name='apprequest',
            name='events',
            field=models.ManyToManyField(to='omaha.Event'),
            preserve_default=True,
        ),
    ]
