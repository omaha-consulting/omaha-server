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

from freezegun import freeze_time

from crash.models import Crash
from crash.tasks import processing_crash_dump
from omaha.tests.utils import temporary_media_root


BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
SYM_FILE = os.path.join(TEST_DATA_DIR, 'BreakpadTestApp.sym')
CRASH_DUMP_FILE = os.path.join(TEST_DATA_DIR, '7b05e196-7e23-416b-bd13-99287924e214.dmp')
SYMBOLS_PATH = os.path.join(TEST_DATA_DIR, 'symbols')
STACKTRACE_PATH = os.path.join(TEST_DATA_DIR, 'stacktrace.txt')


class CrashModelTest(test.TestCase):
    @temporary_media_root(
        MEDIA_URL='http://omaha-test.s3.amazonaws.com/',
        CRASH_S3_MOUNT_PATH=TEST_DATA_DIR,
        CRASH_SYMBOLS_PATH=SYMBOLS_PATH,
    )
    @freeze_time("2014-12-11")
    def test_model(self):
        meta = dict(
            lang='en',
            version='1.0.0.1',
        )
        app_id = '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
        user_id = '{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}',
        with open(CRASH_DUMP_FILE) as f:
            obj = Crash.objects.create(
                app_id=app_id,
                user_id=user_id,
                mini_dump=SimpleUploadedFile('7b05e196-7e23-416b-bd13-99287924e214.dmp', f.read()),
                meta=meta,
            )

        self.assertIsNone(obj.stacktrace)
        processing_crash_dump(obj.pk)

        with open(STACKTRACE_PATH, 'rb') as f:
            stacktrace = f.read()

        crash = Crash.objects.get(pk=obj.pk)
        self.assertEqual(crash.stacktrace, stacktrace)
        self.assertIsNotNone(crash.stacktrace_json)
        self.assertEqual(crash.stacktrace_json['crash_info']['type'], 'EXCEPTION_ACCESS_VIOLATION_WRITE')
