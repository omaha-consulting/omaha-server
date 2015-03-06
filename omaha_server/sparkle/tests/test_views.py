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
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from xmlunittest import XmlTestMixin
from freezegun import freeze_time

from omaha.tests.utils import temporary_media_root
from omaha.factories import ApplicationFactory, ChannelFactory

from sparkle.tests import fixtures
from sparkle.factories import SparkleVersionFactory



class SparkleViewTest(TestCase, XmlTestMixin):
    def setUp(self):
        self.client = Client()

    @freeze_time('2014-10-14 08:28:05')
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_sparkle(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='chrome')
        channel = ChannelFactory.create(name='stable')
        obj = SparkleVersionFactory.create(
            app=app,
            channel=channel,
            version='782.112',
            short_version='13.0.782.112',
            file=SimpleUploadedFile('./chrome.dmg', b'_' * 23963192),
            file_size=23963192)
        obj.save()

        response = self.client.get(reverse('sparkle_appcast', args=(app.name, channel.name)),
                                   HTTP_HOST='example.com')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_sparkle)

    @freeze_time('2014-10-14 08:28:05')
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_sparkle_with_dsa_signature(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C9C}', name='chrome_dsa')
        channel = ChannelFactory.create(name='stable')
        obj = SparkleVersionFactory.create(
            app=app,
            channel=channel,
            version='782.112',
            short_version='13.0.782.112',
            dsa_signature='MCwCFCdoW13VBGJWIfIklKxQVyetgxE7AhQTVuY9uQT0KOV1UEk21epBsGZMPg==',
            file=SimpleUploadedFile('./chrome.dmg', b'_' * 23963192),
            file_size=23963192)
        obj.save()

        response = self.client.get(reverse('sparkle_appcast', args=(app.name, channel.name)),
                                   HTTP_HOST='example.com')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(fixtures.response_sparkle_with_dsa,
                                        response.content)
