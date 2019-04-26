# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0004_partialupdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='partialupdate',
            name='active_users',
            field=models.PositiveSmallIntegerField(default=1, help_text='Active users in the past ...', choices=[(1, 'week'), (0, 'all'), (2, 'month')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='partialupdate',
            name='exclude_new_users',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
