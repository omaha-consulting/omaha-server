# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0021_grant_permissions_to_public_group'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='action',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='application',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='version',
            options={'ordering': ['id']},
        ),
    ]
