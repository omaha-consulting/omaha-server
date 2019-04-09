# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import models, migrations, connection

def grant_permissions(apps, schema_editor):
    cursor = connection.cursor()

    cursor.execute('GRANT SELECT ON TABLE sparkle_sparkleversion, sparkle_sparkleversion_id_seq '
                   'TO GROUP %s;' % settings.DB_PUBLIC_ROLE)

    cursor.execute('GRANT USAGE, SELECT ON SEQUENCE sparkle_sparkleversion_id_seq '
                   'TO GROUP %s;' % settings.DB_PUBLIC_ROLE)


class Migration(migrations.Migration):

    dependencies = [
        ('sparkle', '0005_auto_20150707_0822'),
        ('omaha', '0021_grant_permissions_to_public_group'),
    ]

    operations = [
        migrations.RunPython(grant_permissions, reverse_code=migrations.RunPython.noop),
    ]
