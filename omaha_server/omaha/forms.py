# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 Crystalnix Limited

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
from django.forms import widgets

from django_ace import AceWidget
from suit.widgets import LinkedSelect
from suit_redactor.widgets import RedactorWidget

from models import Application, Version, Action, Data


__all__ = ['ApplicationAdminForm', 'VersionAdminForm', 'ActionAdminForm']


class ApplicationAdminForm(forms.ModelForm):
    def clean_id(self):
        return self.cleaned_data["id"].upper()

    class Meta:
        model = Application
        exclude = []


class DataAdminForm(forms.ModelForm):
    class Meta:
        model = Data
        exclude = []
        widgets = {
            'value': AceWidget(mode='json', theme='monokai', width='600px', height='300px'),
        }


class VersionAdminForm(forms.ModelForm):
    class Meta:
        model = Version
        exclude = []
        widgets = {
            'app': LinkedSelect,
            'release_notes': RedactorWidget(editor_options={'lang': 'en',
                                                            'minHeight': 150}),
            'file_size': widgets.TextInput(attrs=dict(disabled='disabled')),
        }

    def clean_file_size(self):
        file = self.cleaned_data["file"]
        return file.size


class ActionAdminForm(forms.ModelForm):
    SUCCESSSACTION_CHOICES = (
        ('default', 'default'),
        ('exitsilently', 'exitsilently'),
        ('exitsilentlyonlaunchcmd', 'exitsilentlyonlaunchcmd')
    )
    successsaction = forms.ChoiceField(choices=SUCCESSSACTION_CHOICES)

    class Meta:
        model = Action
        exclude = []