# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations, connection

def grant_permissions(apps, schema_editor):
    cursor = connection.cursor()

    cursor.execute('GRANT SELECT, UPDATE, INSERT ON TABLE feedback_feedback, '
                   'feedback_feedback_id_seq TO GROUP %s;' % settings.DB_PUBLIC_ROLE)

    cursor.execute('GRANT USAGE, SELECT ON SEQUENCE '
                   'feedback_feedback_id_seq TO GROUP %s;' % settings.DB_PUBLIC_ROLE)
    cursor.execute('GRANT USAGE, UPDATE ON SEQUENCE '
                   'feedback_feedback_id_seq TO GROUP %s;' % settings.DB_PUBLIC_ROLE)

class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
        ('omaha', '0021_grant_permissions_to_public_group'),
    ]

    operations = [
        migrations.RunPython(grant_permissions, reverse_code=migrations.RunPython.noop),
    ]
