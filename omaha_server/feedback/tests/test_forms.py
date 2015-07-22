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
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from feedback.forms import FeedbackForm

import logging
IMG_FILE = os.path.join(os.path.dirname(__file__), 'testdata', 'test_png.png')

class FeedbackFormTest(TestCase):
    def test_form(self):
        form_file_data = dict(
            screenshot=SimpleUploadedFile('screenshot.png', content=open(IMG_FILE, 'rb').read()),
            blackbox=SimpleUploadedFile('blackbox.tar', b' '),
            system_logs=SimpleUploadedFile('system_logs.zip', b' '*2),
            attached_file=SimpleUploadedFile('attach.zip', b' '*3),
        )
        form_data = dict(
            description='Test description',
        )

        form = FeedbackForm(form_data, form_file_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['screenshot_size'], 88)
        self.assertEqual(form.cleaned_data['blackbox_size'], 1)
        self.assertEqual(form.cleaned_data['system_logs_size'], 2)
        self.assertEqual(form.cleaned_data['attached_file_size'], 3)


    def test_form_no_description(self):
        form_file_data = dict(
            screenshot=SimpleUploadedFile('screenshot.png', content=open(IMG_FILE, 'rb').read()),
            blackbox=SimpleUploadedFile('blackbox.tar', b' '),
            system_logs=SimpleUploadedFile('system_logs.zip', b' '),
            attached_file=SimpleUploadedFile('attach.zip', b' '),
        )
        form_data = dict(
            email='user@example.com',
            page_url='http://url.com/',
        )

        form = FeedbackForm(form_data, form_file_data)
        self.assertFalse(form.is_valid())
