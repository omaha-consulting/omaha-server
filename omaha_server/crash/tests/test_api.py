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

from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase

from crash.serializers import SymbolsSerializer, CrashSerializer
from crash.models import Symbols, Crash
from crash.factories import SymbolsFactory, CrashFactory

from omaha.tests.utils import temporary_media_root
from omaha.tests.test_api import BaseTest
from omaha_server.utils import is_private


BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
SYM_FILE = os.path.join(TEST_DATA_DIR, 'BreakpadTestApp.sym')


class SymbolsTest(BaseTest, APITestCase):
    url = 'symbols-list'
    url_detail = 'symbols-detail'
    factory = SymbolsFactory
    serializer = SymbolsSerializer

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_detail(self):
        super(SymbolsTest, self).test_detail()

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_list(self):
        super(SymbolsTest, self).test_list()

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_create(self):
        with open(SYM_FILE, 'rb') as f:
            data = dict(file=SimpleUploadedFile('./BreakpadTestApp.sym', f.read()))
        response = self.client.post(reverse(self.url), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        symbols = Symbols.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(symbols).data)
        self.assertEqual(symbols.debug_id, 'C1C0FA629EAA4B4D9DD2ADE270A231CC1')
        self.assertEqual(symbols.debug_file, 'BreakpadTestApp.pdb')

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_create_without_file(self):
        data = dict()
        response = self.client.post(reverse(self.url), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'file': [u'No file was submitted.']})

    @is_private()
    def test_duplicate(self):
        with open(SYM_FILE, 'rb') as f:
            data = dict(file=SimpleUploadedFile('./BreakpadTestApp.sym', f.read()))
        response = self.client.post(reverse(self.url), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        with open(SYM_FILE, 'rb') as f:
            data = dict(file=SimpleUploadedFile('./BreakpadTestApp.sym', f.read()))
        response = self.client.post(reverse(self.url), data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['message'], 'Duplicate symbol')

class CrashTest(BaseTest, APITestCase):
    url = 'crash-list'
    url_detail = 'crash-detail'
    factory = CrashFactory
    serializer = CrashSerializer

    @is_private()
    def test_list(self):
        response = self.client.get(reverse(self.url), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)
        self.assertEqual(self.serializer(self.objects, many=True).data, response.data['results'][::-1])

    @is_private()
    def test_create(self):
        response = self.client.post(reverse(self.url), {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
