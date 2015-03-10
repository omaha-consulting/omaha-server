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

from unittest import TestCase
from xmlunittest import XmlTestMixin

from omaha.tests import fixtures


BASE_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(BASE_DIR, 'fixtures')
REQUEST_XSD_FILE = os.path.join(BASE_DIR, '..', 'request.xsd')
RESPONSE_XSD_FILE = os.path.join(BASE_DIR, '..', 'response.xsd')


class TestRequestScheme(TestCase, XmlTestMixin):
    xsd_path = REQUEST_XSD_FILE

    def test_request_update_check(self):
        root = self.assertXmlDocument(fixtures.request_update_check)
        self.assertXmlValidXSchema(root, filename=self.xsd_path)

    def test_request_event(self):
        root = self.assertXmlDocument(fixtures.request_event)
        self.assertXmlValidXSchema(root, filename=self.xsd_path)

    def test_request_data(self):
        root = self.assertXmlDocument(fixtures.request_data)
        self.assertXmlValidXSchema(root, filename=self.xsd_path)


class TestResponseScheme(TestCase, XmlTestMixin):
    xsd_path = RESPONSE_XSD_FILE

    def test_response_update_check_negative(self):
        root = self.assertXmlDocument(fixtures.response_update_check_negative)
        self.assertXmlValidXSchema(root, filename=self.xsd_path)

    def test_response_update_check_positive(self):
        root = self.assertXmlDocument(fixtures.response_update_check_positive)
        self.assertXmlValidXSchema(root, filename=self.xsd_path)

    def test_response_event(self):
        root = self.assertXmlDocument(fixtures.response_event)
        self.assertXmlValidXSchema(root, filename=self.xsd_path)

    def test_response_data(self):
        root = self.assertXmlDocument(fixtures.response_data_doc)
        self.assertXmlValidXSchema(root, filename=self.xsd_path)
