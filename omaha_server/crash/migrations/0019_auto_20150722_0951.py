# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_crashes_sizes(apps, schema_editor):
    Crash = apps.get_model("crash", "Crash")
    crashes = Crash.objects.iterator()
    for crash in crashes:
        crash.archive_size = crash.archive.size if crash.archive else 0
        crash.minidump_size = crash.upload_file_minidump.size if crash.upload_file_minidump else 0
        crash.save()


def set_symbols_size(apps, schema_editor):
    Symbol = apps.get_model("crash", "Symbols")
    symbols = Symbol.objects.iterator()
    for symbol in symbols:
        symbol.file_size = symbol.file.size if symbol.file else 0
        symbol.save()


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0018_auto_20150707_0822'),
    ]

    operations = [
        migrations.AddField(
            model_name='crash',
            name='archive_size',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='crash',
            name='minidump_size',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.RunPython(
            set_crashes_sizes,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.AddField(
            model_name='symbols',
            name='file_size',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.RunPython(
            set_symbols_size,
            reverse_code=migrations.RunPython.noop
        ),
    ]
