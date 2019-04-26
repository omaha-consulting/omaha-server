# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import django_extensions.db.fields
import feedback.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('description', models.TextField()),
                ('email', models.CharField(max_length=500, null=True, blank=True)),
                ('page_url', models.CharField(max_length=500, null=True, blank=True)),
                ('screenshot', models.ImageField(null=True, upload_to=feedback.models.screenshot_upload_to, blank=True)),
                ('blackbox', models.FileField(null=True, upload_to=feedback.models.blackbox_upload_to, blank=True)),
                ('system_logs', models.FileField(null=True, upload_to=feedback.models.logs_upload_to, blank=True)),
                ('attached_file', models.FileField(null=True, upload_to=feedback.models.attach_upload_to, blank=True)),
                ('feedback_data', jsonfield.fields.JSONField(help_text='JSON format', null=True, verbose_name='Feedback data', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
