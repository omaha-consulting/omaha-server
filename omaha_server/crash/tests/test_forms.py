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

import os

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from crash.forms import SymbolsAdminForm, CrashFrom


BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
SYM_FILE = os.path.join(TEST_DATA_DIR, 'BreakpadTestApp.sym')
TAR_FILE = os.path.join(TEST_DATA_DIR, 'foo.tar')


class SymbolsAdminFormTest(TestCase):
    def test_form(self):
        form_data = {}

        with open(SYM_FILE, 'rb') as f:
            form_file_data = {'file': SimpleUploadedFile('BreakpadTestApp.sym', f.read())}

        form = SymbolsAdminForm(form_data, form_file_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['debug_id'], 'C1C0FA629EAA4B4D9DD2ADE270A231CC1')
        self.assertEqual(form.cleaned_data['debug_file'], 'BreakpadTestApp.pdb')
        self.assertEqual(form.cleaned_data['file_size'], 68149)


class CrashFormTest(TestCase):
    def test_form(self):
        form_file_data = dict(upload_file_minidump=SimpleUploadedFile(
            "7b05e196-7e23-416b-bd13-99287924e214.dmp", b"content"))
        form_data = dict(
            appid='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
            userid='{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}',
        )

        form = CrashFrom(form_data, form_file_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['upload_file_minidump'].name, '7b05e196-7e23-416b-bd13-99287924e214.dmp')
        self.assertEqual(form.cleaned_data['archive_size'], 0)
        self.assertEqual(form.cleaned_data['minidump_size'], 7)

    def test_form_tar_file(self):
        with open(TAR_FILE, 'rb') as f:
            form_file_data = dict(upload_file_minidump=SimpleUploadedFile(
                "foo.tar", f.read()))
        form_data = dict(
            appid='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
            userid='{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}',
        )

        form = CrashFrom(form_data, form_file_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['upload_file_minidump'].name, '7b05e196-7e23-416b-bd13-99287924e214.dmp')
        self.assertEqual(form.cleaned_data['archive'].name, 'foo.tar')
        self.assertEqual(form.cleaned_data['archive_size'], 85504)
        self.assertEqual(form.cleaned_data['minidump_size'], 14606)