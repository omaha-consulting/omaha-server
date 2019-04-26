# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0019_grant_permissions_to_public_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='crash',
            name='ip',
            field=models.IPAddressField(null=True, blank=True),
        ),
    ]
