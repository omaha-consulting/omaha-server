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
from django.test.client import RequestFactory

from omaha.templatetags.url_replace import url_replace


class UrlReplaceTagTest(TestCase):
    def test_url_replace(self):
        rf = RequestFactory()
        request = rf.get('/', {'param': 'value'})
        res = url_replace(request, 'page', 10)
        self.assertSetEqual(set(res.split('&')), set('page=10&param=value'.split('&')))
