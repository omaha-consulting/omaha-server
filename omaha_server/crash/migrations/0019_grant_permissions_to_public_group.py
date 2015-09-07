# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations, connection

def grant_permissions(apps, schema_editor):
    cursor = connection.cursor()

    cursor.execute('GRANT SELECT, INSERT, UPDATE ON TABLE crash_crash, crash_crash_id_seq, '
                   'crash_crashdescription, crash_crashdescription_id_seq '
                   'TO GROUP %s;' % settings.DB_PUBLIC_ROLE)
    cursor.execute('GRANT SELECT ON TABLE crash_symbols, '
                   'crash_symbols_id_seq TO GROUP %s;' % settings.DB_PUBLIC_ROLE)

    cursor.execute('GRANT USAGE, SELECT ON SEQUENCE crash_crash_id_seq '
                   'TO GROUP %s;' % settings.DB_PUBLIC_ROLE)
    cursor.execute('GRANT USAGE, SELECT ON SEQUENCE crash_crashdescription_id_seq '
                   'TO GROUP %s;' % settings.DB_PUBLIC_ROLE)


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0018_auto_20150707_0822'),
        ('omaha', '0021_grant_permissions_to_public_group'),
    ]

    operations = [
        migrations.RunPython(grant_permissions, reverse_code=migrations.RunPython.noop),
    ]
