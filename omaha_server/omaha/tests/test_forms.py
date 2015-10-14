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

from collections import OrderedDict

from django.test import TestCase, override_settings

from omaha.forms import ApplicationAdminForm, ManualCleanupForm, CrashManualCleanupForm

import mock


class ApplicationAdminFormTest(TestCase):
    def test_form(self):
        app_id = '{5fad27d4-6bfa-4daa-a1b3-5a1f821fee0f}'
        form_data = dict(id=app_id, name='test')
        form = ApplicationAdminForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['id'], app_id.upper())
        self.assertEqual(form.cleaned_data['name'], 'test')



class ManualCleanupFormTest(TestCase):
    def test_form(self):
        data = dict(limit_days=10, limit_size=10)
        form = ManualCleanupForm(data=data, initial=dict(type='feedback__Feedback'))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['limit_days'], 10)
        self.assertEqual(form.cleaned_data['limit_size'], 10)
        self.assertEqual(type(form.fields), OrderedDict)
        self.assertEqual(form.fields.keys(), ['limit_days', 'limit_size'])

        with mock.patch('omaha.tasks.deferred_manual_cleanup.apply_async') as mocked:
            form.cleanup()
        mock_args, mock_kwargs = mocked.call_args

        self.assertTrue(mocked.called)
        self.assertDictEqual(mock_args[1], data)

    def test_negative_fields(self):
        data = dict(limit_days=-1, limit_size=-1)
        form = ManualCleanupForm(data=data, initial=dict(type='feedback__Feedback'))

        self.assertFalse(form.is_valid())
        self.assertItemsEqual(form.errors.keys(), ['limit_size', 'limit_days'])


class CrashManualCleanupFormTest(TestCase):
    def test_form(self):
        data = dict(limit_days=10, limit_size=10, limit_duplicated=10)
        form = CrashManualCleanupForm(data=data, initial=dict(type='crash__Crash'))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['limit_days'], 10)
        self.assertEqual(form.cleaned_data['limit_size'], 10)
        self.assertEqual(form.cleaned_data['limit_duplicated'], 10)
        self.assertEqual(type(form.fields), OrderedDict)
        self.assertEqual(form.fields.keys(), ['limit_duplicated', 'limit_days', 'limit_size'])

        with mock.patch('omaha.tasks.deferred_manual_cleanup.apply_async') as mocked:
            form.cleanup()
        mock_args, mock_kwargs = mocked.call_args

        self.assertTrue(mocked.called)
        self.assertDictEqual(mock_args[1], data)

    def test_negative_fields(self):
        data = dict(limit_days=-1, limit_size=-1, limit_duplicated=-1)
        form = CrashManualCleanupForm(data=data, initial=dict(type='crash__Crash'))

        self.assertFalse(form.is_valid())
        self.assertItemsEqual(form.errors.keys(), ['limit_duplicated', 'limit_days', 'limit_size'])
