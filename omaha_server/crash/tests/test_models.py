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

from django import test
from django.core.files.uploadedfile import SimpleUploadedFile

from crash.models import Crash, Symbols, symbols_upload_to
from omaha.tests.utils import temporary_media_root
from omaha.factories import VersionFactory


BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
SYM_FILE = os.path.join(TEST_DATA_DIR, 'BreakpadTestApp.sym')


class CrashModelTest(test.TestCase):
    @temporary_media_root()
    def test_model(self):
        meta = dict(
            lang='en',
            version='1.0.0.1',
        )
        app_id = '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
        user_id = '{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}',
        obj = Crash.objects.create(
            app_id=app_id,
            user_id=user_id,
            mini_dump=SimpleUploadedFile('./dump.dat', False),
            meta=meta,
        )

        self.assertTrue(obj)
        self.assertDictEqual(obj.meta, meta)
        self.assertEqual(obj.app_id, app_id)
        self.assertEqual(obj.user_id, user_id)


class SymbolsModelTest(test.TestCase):
    @temporary_media_root()
    def setUp(self):
        self.version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', b''))

    @temporary_media_root()
    def test_model(self):
        with open(SYM_FILE, 'rb') as f:
            obj = Symbols.objects.create(
                debug_file='BreakpadTestApp.pdb',
                debug_id='C1C0FA629EAA4B4D9DD2ADE270A231CC1',
                version=self.version,
                file=SimpleUploadedFile(f.name, f.read()),
            )
        self.assertTrue(obj)

    @temporary_media_root()
    def test_symbols_upload_to(self):
        with open(SYM_FILE, 'rb') as f:
            obj = Symbols.objects.create(
                debug_file='BreakpadTestApp.pdb',
                debug_id='C1C0FA629EAA4B4D9DD2ADE270A231CC1',
                version=self.version,
                file=SimpleUploadedFile(f.name, f.read()),
            )
        self.assertIn('symbols/BreakpadTestApp.pdb/C1C0FA629EAA4B4D9DD2ADE270A231CC1/BreakpadTestApp.sym',
                      obj.file.url)

        self.assertEqual(symbols_upload_to(obj, 'BreakpadTestApp.pdb'),
                         'symbols/BreakpadTestApp.pdb/C1C0FA629EAA4B4D9DD2ADE270A231CC1/BreakpadTestApp.sym')


