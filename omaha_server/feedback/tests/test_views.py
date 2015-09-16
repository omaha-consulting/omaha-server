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
from django.core.urlresolvers import reverse
from django.conf import settings

from feedback.models import Feedback


BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
PB_FILE = os.path.join(TEST_DATA_DIR, 'request.pb')
DESC_ONLY_FILE = os.path.join(TEST_DATA_DIR, 'description_only.pb')
NO_DESC_FILE = os.path.join(TEST_DATA_DIR, 'no_description.pb')


class FeedbackViewTest(test.TestCase):
    def test_view(self):
        with open(PB_FILE, 'rb') as f:
            body = f.read()
        description = 'Testable issue\nwith multiple lines\nof code'
        email = 'user@example.com'
        page_url = 'chrome://newtab/'

        self.assertEqual(Feedback.objects.all().count(), 0)
        response = self.client.post(
            reverse('feedback'),
            data=body,
            content_type='application/x-protobuf',
            REMOTE_ADDR="8.8.8.8"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.all().count(), 1)
        obj = Feedback.objects.get()
        self.assertEqual(response.content.decode(), str(obj.pk))
        self.assertEqual(obj.description, description)
        self.assertEqual(obj.email, email)
        self.assertEqual(obj.page_url, page_url)
        self.assertTrue(obj.screenshot)
        self.assertTrue(obj.blackbox)
        self.assertTrue(obj.system_logs)
        self.assertTrue(obj.attached_file)
        self.assertTrue(obj.feedback_data)
        self.assertEqual(obj.ip, "8.8.8.8")

    def test_view_empty_ip(self):
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
            with open(PB_FILE, 'rb') as f:
                body = f.read()
            description = 'Testable issue\nwith multiple lines\nof code'
            email = 'user@example.com'
            page_url = 'chrome://newtab/'

            self.assertEqual(Feedback.objects.all().count(), 0)
            response = self.client.post(
                reverse('feedback'),
                data=body,
                content_type='application/x-protobuf',
                REMOTE_ADDR=""
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Feedback.objects.all().count(), 1)
            obj = Feedback.objects.get()
            self.assertEqual(response.content.decode(), str(obj.pk))
            self.assertEqual(obj.description, description)
            self.assertEqual(obj.email, email)
            self.assertEqual(obj.page_url, page_url)
            self.assertTrue(obj.screenshot)
            self.assertTrue(obj.blackbox)
            self.assertTrue(obj.system_logs)
            self.assertTrue(obj.attached_file)
            self.assertTrue(obj.feedback_data)
            self.assertEqual(obj.ip, None)

    def test_view_desc_only(self):
        with open(DESC_ONLY_FILE, 'rb') as f:
            body = f.read()
        description = 'Description only'

        self.assertEqual(Feedback.objects.all().count(), 0)
        response = self.client.post(
            reverse('feedback'),
            data=body,
            content_type='application/x-protobuf'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.all().count(), 1)
        obj = Feedback.objects.get()
        self.assertEqual(response.content.decode(), str(obj.pk))
        self.assertEqual(obj.description, description)
        self.assertEqual(obj.email, '')
        self.assertEqual(obj.page_url, '')
        self.assertFalse(obj.screenshot)
        self.assertFalse(obj.blackbox)
        self.assertFalse(obj.system_logs)
        self.assertFalse(obj.attached_file)
        self.assertTrue(obj.feedback_data)

    def test_view_invalid(self):
        with open(NO_DESC_FILE, 'rb') as f:
            body = f.read()

        # No description provided - form is not valid
        self.assertEqual(Feedback.objects.all().count(), 0)
        with self.assertRaises(NotImplementedError):
            self.client.post(
                reverse('feedback'),
                data=body,
                content_type='application/x-protobuf'
            )
        self.assertEqual(Feedback.objects.all().count(), 0)

        # Fail to parse protobuf messages
        with self.assertRaises(BaseException):
            self.client.post(
                reverse('feedback'),
                data={},
            )
        self.assertEqual(Feedback.objects.all().count(), 0)
