# coding: utf8

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from xmlunittest import XmlTestMixin
from freezegun import freeze_time

import fixtures


class UpdateViewTest(TestCase, XmlTestMixin):
    def setUp(self):
        self.client = Client()

    @freeze_time('2014-01-01 15:41:48')  # 56508 sec
    def test_updatecheck_negative(self):
        response = self.client.post(reverse('update'),
                                    fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_update_check_negative)
