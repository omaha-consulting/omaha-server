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

from crash.models import Symbols
from crash.serializers import SymbolsSerializer


BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
SYM_FILE = os.path.join(TEST_DATA_DIR, 'BreakpadTestApp.sym')


class AppSerializerTest(TestCase):
    def test_serializer(self):
        data = dict(file=SimpleUploadedFile('./test.pdb', False),
                    debug_id='C1C0FA629EAA4B4D9DD2ADE270A231CC1',
                    debug_file='BreakpadTestApp.pdb')
        symbols = Symbols.objects.create(**data)
        self.assertDictEqual(SymbolsSerializer(symbols).data,
                             dict(id=symbols.id,
                                  debug_id='C1C0FA629EAA4B4D9DD2ADE270A231CC1',
                                  debug_file='BreakpadTestApp.pdb',
                                  file=symbols.file.url,
                                  created=symbols.created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                                  modified=symbols.modified.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), ))

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_auto_fill_file_size(self):
        with open(SYM_FILE, 'rb') as f:
            data = dict(file=SimpleUploadedFile('./BreakpadTestApp.sym', f.read()))

        symbols = SymbolsSerializer(data=data)
        self.assertTrue(symbols.is_valid())
        symbols_instance = symbols.save()
        self.assertEqual(symbols_instance.debug_id, 'C1C0FA629EAA4B4D9DD2ADE270A231CC1')
        self.assertEqual(symbols_instance.debug_file, 'BreakpadTestApp.pdb')
