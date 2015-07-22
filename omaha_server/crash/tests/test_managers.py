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

from django.test import TestCase

from crash.models import Crash, Symbols
from crash.factories import CrashFactory, SymbolsFactory



class CrashManagerTest(TestCase):
    def test_get_size(self):
        archive_size = 10
        minidump_size = 20
        CrashFactory.create_batch(10, archive_size=archive_size, minidump_size=minidump_size)
        size = Crash.objects.get_size()
        self.assertEqual(size, (archive_size + minidump_size) * 10)


class SymbolsManagerTest(TestCase):
    def test_get_size(self):
        file_size = 42
        SymbolsFactory.create_batch(10, file_size=file_size)
        size = Symbols.objects.get_size()
        self.assertEqual(size, file_size * 10)
