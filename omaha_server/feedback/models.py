# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2015 Crystalnix Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""

import os
import uuid

from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from jsonfield import JSONField

from omaha.models import BaseModel
from feedback.managers import FeedbackManager


def upload_to(directory, obj, filename):
    now = timezone.now()
    max_length = 100
    path = os.path.join(*list(map(str, [directory, now.year, now.month,
                                   now.day, uuid.uuid4(), filename])))
    if len(path) > max_length:
        name, ext = os.path.splitext(path)
        ext_length = len(ext)
        path = name[:max_length-ext_length] + ext
    return path


def screenshot_upload_to(obj, filename):
    return upload_to('screenshot', obj, filename)


def blackbox_upload_to(obj, filename):
    return upload_to('blackbox', obj, filename)


def logs_upload_to(obj, filename):
    return upload_to('system_logs', obj, filename)


def attach_upload_to(obj, filename):
    return upload_to('feedback_attach', obj, filename)


class Feedback(BaseModel):
    description = models.TextField()
    email = models.CharField(max_length=500, null=True, blank=True)
    page_url = models.CharField(max_length=2048, null=True, blank=True)
    screenshot = models.ImageField(upload_to=screenshot_upload_to, blank=True, null=True)
    screenshot_size = models.PositiveIntegerField(null=True, blank=True)
    blackbox = models.FileField(upload_to=blackbox_upload_to, blank=True, null=True)
    blackbox_size = models.PositiveIntegerField(null=True, blank=True)
    system_logs = models.FileField(upload_to=logs_upload_to, blank=True, null=True)
    system_logs_size = models.PositiveIntegerField(null=True, blank=True)
    attached_file = models.FileField(upload_to=attach_upload_to, blank=True, null=True)
    attached_file_size = models.PositiveIntegerField(null=True, blank=True)
    feedback_data = JSONField(verbose_name='Feedback data', help_text='JSON format', null=True, blank=True)
    ip = models.GenericIPAddressField(blank=True, null=True, protocol='IPv4')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FeedbackManager()

    @property
    def size(self):
         return self.screenshot_size + self.blackbox_size + self.system_logs_size + self.attached_file_size


class FeedbackDescription(Feedback):
    class Meta:
        proxy = True


def pre_feedback_save(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        if old.screenshot != instance.screenshot:
            old.screenshot.delete(save=False)
            old.screenshot_size = 0
        if old.blackbox != instance.blackbox:
            old.blackbox.delete(save=False)
            old.blackbox_size = 0
        if old.system_logs != instance.system_logs:
            old.system_logs.delete(save=False)
            old.system_logs_size = 0
        if old.attached_file != instance.attached_file:
            old.attached_file.delete(save=False)
            old.attached_file_size = 0


def pre_feedback_delete(sender, instance, **kwargs):
    file_fields = [instance.screenshot, instance.blackbox, instance.system_logs, instance.attached_file]
    for field in file_fields:
        storage, name = field.storage, field.name
        if name:
            storage.delete(name)


def get_subclasses(cls):
    result = [cls]
    classes_to_inspect = [cls]
    while classes_to_inspect:
        class_to_inspect = classes_to_inspect.pop()
        for subclass in class_to_inspect.__subclasses__():
            if subclass not in result:
                result.append(subclass)
                classes_to_inspect.append(subclass)
    return result

for subclass in get_subclasses(Feedback):
    pre_delete.connect(pre_feedback_delete, subclass)
    pre_save.connect(pre_feedback_save, subclass)
