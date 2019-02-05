# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import omaha.fields


class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0001_initial'),
    ]

    operations = [
        migrations.RenameField('Action', 'successsaction', 'onsuccess'),
    ]
