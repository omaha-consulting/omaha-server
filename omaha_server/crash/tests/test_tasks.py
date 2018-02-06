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
from django.core.files.storage import DefaultStorage

from clom.shell import CommandError
from mock import patch
from freezegun import freeze_time

from crash.models import Crash
from crash.tasks import processing_crash_dump, get_sentry_link
from omaha.tests.utils import temporary_media_root


BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
SYM_FILE = os.path.join(TEST_DATA_DIR, 'BreakpadTestApp.sym')
CRASH_DUMP_FILE = os.path.join(TEST_DATA_DIR, '7b05e196-7e23-416b-bd13-99287924e214.dmp')
INCORRECT_CRASH_DUMP_FILE = os.path.join(TEST_DATA_DIR, 'incorrect_minidump.dmp')
SYMBOLS_PATH = os.path.join(TEST_DATA_DIR, 'symbols')
STACKTRACE_PATH = os.path.join(TEST_DATA_DIR, 'stacktrace.txt')


class CrashModelTest(test.TestCase):
    @temporary_media_root(
        MEDIA_URL='http://omaha-test.s3.amazonaws.com/',
        CRASH_S3_MOUNT_PATH=TEST_DATA_DIR,
        CRASH_SYMBOLS_PATH=SYMBOLS_PATH,
    )
    @test.override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=False,)
    @freeze_time("2014-12-11")
    @patch('crash.utils.send_stacktrace')
    @patch('crash.utils.crash_sender')
    @patch('uuid.uuid4', lambda: '92d51f8b-f67a-4d80-ac7f-9ab8018297d9')
    def test_model(self, mock_send_stacktrace, mock_client):
        meta = dict(
            lang='en',
            ver='1.0.0.1',
            channel='alpha'
        )
        app_id = '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}'
        user_id = '{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}'
        with open(CRASH_DUMP_FILE, 'rb') as f:
            obj = Crash.objects.create(
                appid=app_id,
                userid=user_id,
                upload_file_minidump=SimpleUploadedFile('7b05e196-7e23-416b-bd13-99287924e214.dmp', f.read()),
                meta=meta,
            )

        self.assertIsNone(obj.stacktrace)
        processing_crash_dump(obj.pk)

        with open(STACKTRACE_PATH, 'rb') as f:
            stacktrace = f.read()

        crash = Crash.objects.get(pk=obj.pk)
        self.assertEqual(crash.stacktrace, stacktrace.decode())
        self.assertIsNotNone(crash.stacktrace_json)
        self.assertEqual(crash.stacktrace_json['crash_info']['type'], 'EXCEPTION_ACCESS_VIOLATION_WRITE')
        self.assertEqual(crash.signature, 'crashedFunc()')
        self.assertEqual(crash.os, 'Windows NT')
        self.assertEqual(crash.build_number, '1.0.0.1')
        self.assertEqual(crash.channel, 'alpha')

    @temporary_media_root(
        MEDIA_URL='http://omaha-test.s3.amazonaws.com/',
        CRASH_S3_MOUNT_PATH=TEST_DATA_DIR,
        CRASH_SYMBOLS_PATH=SYMBOLS_PATH,
    )
    @freeze_time("2014-12-11")
    @patch('crash.utils.send_stacktrace')
    @patch('crash.utils.crash_sender')
    @patch('uuid.uuid4', lambda: '92d51f8b-f67a-4d80-ac7f-9ab8018297d9')
    def test_incorrect_dump(self, mock_send_stacktrace, mock_client):
        meta = dict(
            lang='en',
            ver='1.0.0.1',
        )
        app_id = '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}'
        user_id = '{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}'
        with open(INCORRECT_CRASH_DUMP_FILE, 'rb') as f:
            obj = dict(
                appid=app_id,
                userid=user_id,
                upload_file_minidump=SimpleUploadedFile('incorrect_minidump.dmp', f.read()),
                meta=meta,
            )
            self.assertRaises(CommandError, Crash.objects.create, **obj)

    @temporary_media_root(
        MEDIA_URL='http://omaha-test.s3.amazonaws.com/',
        CRASH_S3_MOUNT_PATH=TEST_DATA_DIR,
        CRASH_SYMBOLS_PATH=SYMBOLS_PATH,
    )
    @test.override_settings(CELERY_ALWAYS_EAGER=False,)
    @freeze_time("2014-12-11")
    @patch('crash.utils.send_stacktrace', lambda: None)
    @patch('crash.utils.crash_sender')
    @patch('uuid.uuid4', lambda: '92d51f8b-f67a-4d80-ac7f-9ab8018297d9')
    def test_get_sentry_link(self, mock_client):
        meta = dict(
            lang='en',
            ver='1.0.0.1',
        )
        app_id = '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}'
        user_id = '{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}'
        with open(CRASH_DUMP_FILE, 'rb') as f:
            obj = Crash.objects.create(
                appid=app_id,
                userid=user_id,
                upload_file_minidump=SimpleUploadedFile('7b05e196-7e23-416b-bd13-99287924e214.dmp', f.read()),
                meta=meta,
            )
        with patch('requests.get') as mocked:
            instance = mocked.return_value
            instance.json.return_value = {'groupID': '1', 'id': '2'}
            get_sentry_link(obj.pk, '123')
        obj = Crash.objects.get(id=obj.id)
        self.assertEqual(obj.eventid, '2')
        self.assertEqual(obj.groupid, '1')
