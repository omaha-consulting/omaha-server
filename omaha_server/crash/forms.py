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

import tarfile

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import widgets

from django_ace import AceWidget
from crash.models import Symbols
from models import Crash
from utils import parse_debug_meta_info


class CrashFrom(forms.ModelForm):
    class Meta:
        model = Crash
        exclude = []
        widgets = {
            'stacktrace_json': AceWidget(mode='json', theme='monokai', width='600px', height='300px'),
            'stacktrace': AceWidget(theme='monokai', width='600px', height='300px'),
            'meta': AceWidget(mode='json', theme='monokai', width='600px', height='300px'),
        }

    def clean_archive(self):
        return self.cleaned_data.get('archive_file')

    def clean_upload_file_minidump(self):
        file = self.cleaned_data["upload_file_minidump"]

        if file.name.endswith('.tar'):
            t_file = tarfile.open(fileobj=file, mode='r')
            self.cleaned_data['archive_file'] = file
            dump_name = filter(lambda i: i.endswith('.dmp'), t_file.getnames())
            if dump_name:
                file = t_file.extractfile(dump_name[0])
                file = SimpleUploadedFile(file.name, file.read())
            else:
                raise forms.ValidationError(u"The archive does not contain a valid crash dump file.")

        return file


class SymbolsFileInput(forms.ClearableFileInput):
    url_markup_template = '<a href="{0}">Link</a>'


class SymbolsFileField(forms.Field):
    widget = SymbolsFileInput


class SymbolsAdminForm(forms.ModelForm):
    file = SymbolsFileField()

    class Meta:
        model = Symbols
        exclude = []
        widgets = {
            'debug_id': widgets.TextInput(attrs=dict(disabled='disabled')),
            'debug_file': widgets.TextInput(attrs=dict(disabled='disabled')),
        }

    def clean_file(self):
        file = self.cleaned_data["file"]
        try:
            head = file.readline().rstrip()
            meta = parse_debug_meta_info(head, exception=forms.ValidationError)
            self.cleaned_data.update(meta)
        except:
            raise forms.ValidationError(u"The file contains invalid data.")
        return file
