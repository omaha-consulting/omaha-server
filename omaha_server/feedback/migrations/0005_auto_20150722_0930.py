# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from django.conf import settings


def set_feedbacks_size(apps, schema_editor):
    Feedback = apps.get_model("feedback", "Feedback")
    feedbacks = Feedback.objects.iterator()
    for feedback in feedbacks:
        feedback.screenshot_size = feedback.screenshot.size if feedback.screenshot else 0
        feedback.attached_file_size = feedback.attached_file.size if feedback.attached_file else 0
        feedback.blackbox_size = feedback.blackbox.size if feedback.blackbox else 0
        feedback.system_logs_size = feedback.system_logs.size if feedback.system_logs else 0
        feedback.save()


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0004_auto_20150917_0932'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='attached_file_size',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='blackbox_size',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='screenshot_size',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='system_logs_size',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.RunPython(
            set_feedbacks_size,
            reverse_code=migrations.RunPython.noop
        ),
    ]
