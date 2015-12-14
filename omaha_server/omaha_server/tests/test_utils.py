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
from django.test import override_settings
from mock import Mock

from omaha_server.utils import show_toolbar, add_extra_to_log_message, get_splunk_url


class UtilsTest(TestCase):
    def setUp(self):
        self.request = Mock()

    def test_show_toolbar_ajax(self):
        self.request.is_ajax = lambda: True
        self.assertFalse(show_toolbar(self.request))

    @override_settings(DEBUG=True)
    def test_show_toolbar_debug_true(self):
        self.request.is_ajax = lambda: False
        self.assertTrue(show_toolbar(self.request))

    @override_settings(DEBUG=False)
    def test_show_toolbar_debug_false(self):
        self.request.is_ajax = lambda: False
        self.assertFalse(show_toolbar(self.request))

    def test_add_extra_to_log_message(self):
        msg = 'test'
        extra = dict(a=1, c=3, b=2, d=4)
        expected_msg = 'test, a=1 , b=2 , c=3 , d=4'
        actual_msg = add_extra_to_log_message(msg, extra)
        self.assertEqual(actual_msg, expected_msg)

    @override_settings(SPLUNK_HOST='splunk.example.com')
    def test_add_extra_to_log_message(self):
        params = dict(a=1, c=3, b=2, d=4)
        actual_msg = get_splunk_url(params)
        expected_msg = 'http://splunk.example.com/en-US/app/search/search?q=search a=1 b=2 c=3 d=4'
        self.assertEqual(actual_msg, expected_msg)
