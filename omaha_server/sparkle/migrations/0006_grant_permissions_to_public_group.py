# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
    ]

    operations = [
        migrations.RunPython(grant_permissions, reverse_code=migrations.RunPython.noop),
    ]
