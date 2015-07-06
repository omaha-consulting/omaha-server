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

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from omaha.tests.utils import temporary_media_root

from feedback.models import Feedback
from feedback.serializers import FeedbackSerializer



class FeedbackSerializerTest(TestCase):
    maxDiff = None

    @temporary_media_root()
    def test_serializer(self):
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

        feedback = Feedback.objects.create(
            description=description,
            email=email,
            page_url=page_url,
            screenshot=SimpleUploadedFile('./screenshot.png', b''),
            blackbox=SimpleUploadedFile('./blackbox.tar', b''),
            system_logs=SimpleUploadedFile('./sys_logs.zip', b''),
            attached_file=SimpleUploadedFile('./attach.zip', b''),
            feedback_data=feedback_data,
        )

        self.assertDictEqual(FeedbackSerializer(feedback).data,
                             dict(id=feedback.id,
                                  created=feedback.created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                                  modified=feedback.modified.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                                  screenshot=feedback.screenshot.url,
                                  blackbox=feedback.blackbox.url,
                                  system_logs=feedback.system_logs.url,
                                  attached_file=feedback.attached_file.url,
                                  feedback_data=feedback.feedback_data,
                             ))
