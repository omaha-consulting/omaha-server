# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, connection
from django.conf import settings


def get_group(user, cursor):
    tmpl = """SELECT
        rolname
    FROM
        pg_user
    JOIN pg_auth_members ON(
        pg_user.usesysid = pg_auth_members. MEMBER
    )
    JOIN pg_roles ON(
        pg_roles.oid = pg_auth_members.roleid
    )
    WHERE
        pg_user.usename = %s;
    """
    cursor.execute(tmpl, [user])
    row = cursor.fetchone()
    return row[0] if row else ''


def grant_permissions(apps, schema_editor):
    cursor = connection.cursor()

    cursor.execute("select * from pg_catalog.pg_user where usename=%s;", [settings.DB_PUBLIC_USER])
    if not cursor.fetchall():
        cursor.execute("CREATE USER %s WITH PASSWORD '%s';" % (settings.DB_PUBLIC_USER, settings.DB_PUBLIC_PASSWORD))

    cursor.execute("select * from pg_catalog.pg_group where groname=%s;", [settings.DB_PUBLIC_ROLE])
    if not cursor.fetchall():
        cursor.execute("CREATE GROUP %s;" % settings.DB_PUBLIC_ROLE)

    if not get_group(settings.DB_PUBLIC_USER, cursor) == settings.DB_PUBLIC_ROLE:
        cursor.execute("ALTER GROUP %s ADD USER %s;" % (settings.DB_PUBLIC_ROLE, settings.DB_PUBLIC_USER))

    cursor.execute('GRANT SELECT ON TABLE applications, platforms, platforms_id_seq, '
                   'channels, channels_id_seq, versions, versions_id_seq, actions, '
                   'actions_id_seq, omaha_data, omaha_data_id_seq, omaha_partialupdate, '
                   'omaha_partialupdate_id_seq TO GROUP %s;' % settings.DB_PUBLIC_ROLE)

    cursor.execute('GRANT SELECT, INSERT, UPDATE ON TABLE omaha_apprequest, '
                   'omaha_apprequest_id_seq, omaha_apprequest_events, '
                   'omaha_apprequest_events_id_seq, omaha_event, omaha_event_id_seq, omaha_hw, '
                   'omaha_hw_id_seq, omaha_os, omaha_os_id_seq, omaha_request, '
                   'omaha_request_id_seq TO GROUP %s;' % settings.DB_PUBLIC_ROLE)

    # grant permissions to a user for all sequences in a schema
    cursor.execute('GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA public to %s;' % settings.DB_PUBLIC_ROLE)
    cursor.execute('GRANT UPDATE, USAGE ON ALL SEQUENCES IN SCHEMA public to %s;' % settings.DB_PUBLIC_ROLE)

class Migration(migrations.Migration):
    dependencies = [
        ('omaha', '0020_auto_20150710_0913'),
    ]

    operations = [
        migrations.RunPython(grant_permissions, reverse_code=migrations.RunPython.noop),
    ]
