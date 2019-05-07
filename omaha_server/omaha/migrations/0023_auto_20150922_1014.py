# -*- coding: utf-8 -*-


from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0022_auto_20150909_0755'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='ip',
            field=models.GenericIPAddressField(null=True, blank=True),
        ),
    ]
