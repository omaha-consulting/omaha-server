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

from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.forms import widgets
from django_ace import AceWidget

from feedback.models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = []
        widgets = {
            'feedback_data': AceWidget(mode='json', theme='monokai', width='600px', height='300px'),
            'screenshot_size': widgets.TextInput(attrs=dict(disabled='disabled')),
            'system_logs_size': widgets.TextInput(attrs=dict(disabled='disabled')),
            'blackbox_size': widgets.TextInput(attrs=dict(disabled='disabled')),
            'attached_file_size': widgets.TextInput(attrs=dict(disabled='disabled')),
        }

    def clean_screenshot_size(self):
        return self._clean_file_size('screenshot')

    def clean_blackbox_size(self):
        return self._clean_file_size('blackbox')

    def clean_system_logs_size(self):
        return self._clean_file_size('system_logs')

    def clean_attached_file_size(self):
        return self._clean_file_size('attached_file')

    def _clean_file_size(self, file_field):
        if file_field not in self.cleaned_data:
            return 0
        _file = self.cleaned_data[file_field]
        if isinstance(_file, UploadedFile):
            return _file.size
        return self.initial.get("%s_size" % file_field, 0)
