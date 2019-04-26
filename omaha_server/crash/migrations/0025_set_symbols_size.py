# -*- coding: utf-8 -*-


from django.db import models, migrations


def set_symbols_size(apps, schema_editor):
    Symbol = apps.get_model("crash", "Symbols")
    symbols = Symbol.objects.iterator()
    for symbol in symbols:
        symbol.file_size = symbol.file.size if symbol.file else 0
        symbol.save()


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0024_auto_20151216_1245'),
    ]

    operations = [
        migrations.RunPython(
            set_symbols_size,
            reverse_code=migrations.RunPython.noop
        ),
    ]
