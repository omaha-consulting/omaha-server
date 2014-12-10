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

from crash.utils import get_stacktrace


BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
SYMBOLS_PATH = os.path.join(TEST_DATA_DIR, 'symbols')
CRASH_DUMP_PATH = os.path.join(TEST_DATA_DIR, '7b05e196-7e23-416b-bd13-99287924e214.dmp')
STACKTRACE_PATH = os.path.join(TEST_DATA_DIR, 'stacktrace.txt')


class ShTest(test.TestCase):
    def test_get_stacktrace(self):
        with open(STACKTRACE_PATH, 'rb') as f:
            stacktrace = f.read()

        rezult, stderr = get_stacktrace(CRASH_DUMP_PATH)

        self.assertEqual(rezult, stacktrace)

