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

from omaha.tests.utils import temporary_media_root
from omaha.factories import VersionFactory
from crash.forms import SymbolsAdminForm


BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
SYM_FILE = os.path.join(TEST_DATA_DIR, 'BreakpadTestApp.sym')


class SymbolsAdminFormTest(TestCase):
    @temporary_media_root()
    def setUp(self):
        self.version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', b''))

    def test_parse_debug_meta_info(self):
        head = 'MODULE windows x86 C1C0FA629EAA4B4D9DD2ADE270A231CC1 BreakpadTestApp.pdb'
        form = SymbolsAdminForm()
        self.assertDictEqual(form._parse_debug_meta_info(head),
                             dict(debug_id='C1C0FA629EAA4B4D9DD2ADE270A231CC1',
                                  debug_file='BreakpadTestApp.pdb'))

    def test_form(self):
        form_data = {'version': self.version.pk}

        with open(SYM_FILE, 'rb') as f:
            form_file_data = {'file': SimpleUploadedFile('BreakpadTestApp.sym', f.read())}

        form = SymbolsAdminForm(form_data, form_file_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['debug_id'], 'C1C0FA629EAA4B4D9DD2ADE270A231CC1')
        self.assertEqual(form.cleaned_data['debug_file'], 'BreakpadTestApp.pdb')
