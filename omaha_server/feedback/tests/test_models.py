# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2015 Crystalnix Limited

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

from feedback.models import Feedback
from omaha.tests.utils import temporary_media_root


BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
SCREENSHOT_FILE = os.path.join(TEST_DATA_DIR, 'screenshot.png')


class FeedbackModelTest(test.TestCase):
    @temporary_media_root()
    def test_model(self):
        description = 'Test description'
        email = 'me@example.com'
        page_url = 'http://google.com/'
        feedback_data = {
            'web_data': {
                'url': page_url
            },
            'common_data': {
                'description': description,
                'user_email': email,
          }
        }

        obj = Feedback.objects.create(
            description=description,
            email=email,
            page_url=page_url,
            screenshot=SimpleUploadedFile('./screenshot.png', b''),
            blackbox=SimpleUploadedFile('./blackbox.tar', b''),
            system_logs=SimpleUploadedFile('./sys_logs.zip', b''),
            attached_file=SimpleUploadedFile('./attach.zip', b''),
            feedback_data=feedback_data,
        )

        self.assertTrue(obj)
        self.assertEqual(obj.description, description)
        self.assertEqual(obj.email, email)
        self.assertEqual(obj.page_url, page_url)
        self.assertDictEqual(obj.feedback_data, feedback_data)

    def test_property(self):
        description = 'Test description'

        obj = Feedback.objects.create(
            description=description,
            screenshot=SimpleUploadedFile('./screenshot.png', b''),
            screenshot_size=111,
            blackbox=SimpleUploadedFile('./blackbox.tar', b''),
            blackbox_size=222,
            system_logs=SimpleUploadedFile('./sys_logs.zip', b''),
            system_logs_size=333,
            attached_file=SimpleUploadedFile('./attach.zip', b''),
            attached_file_size=444,
        )

        self.assertEqual(obj.size, 111+222+333+444)
