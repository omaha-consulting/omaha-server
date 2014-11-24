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

from omaha.forms import ApplicationAdminForm


class ApplicationAdminFormTest(TestCase):
    def test_form(self):
        app_id = '{5fad27d4-6bfa-4daa-a1b3-5a1f821fee0f}'
        form_data = dict(id=app_id, name='test')
        form = ApplicationAdminForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['id'], app_id.upper())
        self.assertEqual(form.cleaned_data['name'], 'test')
