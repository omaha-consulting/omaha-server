# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sparkle', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparkleversion',
            name='dsa_signature',
            field=models.CharField(max_length=140, null=True, verbose_name='DSA signature', blank=True),
            preserve_default=True,
        ),
    ]
