# -*- coding: utf-8 -*-


from django.db import migrations, connection
from django.conf import settings


def grant_permissions(apps, schema_editor):
    cursor = connection.cursor()
    cursor.execute('GRANT SELECT ON TABLE django_site TO GROUP %s;' % settings.DB_PUBLIC_ROLE)


class Migration(migrations.Migration):
    dependencies = [
        ('omaha', '0025_auto_20151209_1040'),
        ('sites', '0001_initial')
    ]

    operations = [
        migrations.RunPython(grant_permissions, reverse_code=migrations.RunPython.noop),
    ]
