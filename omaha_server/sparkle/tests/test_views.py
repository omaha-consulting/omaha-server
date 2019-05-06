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
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from xmlunittest import XmlTestMixin
from freezegun import freeze_time

from omaha.tests.utils import temporary_media_root
from omaha.tests import OverloadTestStorageMixin
from omaha.factories import ApplicationFactory, ChannelFactory

from sparkle.models import SparkleVersion
from sparkle.tests import fixtures
from sparkle.factories import SparkleVersionFactory


class SparkleViewTest(OverloadTestStorageMixin, TestCase, XmlTestMixin):
    model = SparkleVersion

    def setUp(self):
        self.client = Client()
        super(SparkleViewTest, self).setUp()

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
    def test_sparkle(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='chrome')
        channel = ChannelFactory.create(name='stable')
        obj = SparkleVersionFactory.create(
            app=app,
            channel=channel,
            version='782.112',
            short_version='13.0.782.112',
            minimum_system_version='10.14.4',
            file=SimpleUploadedFile('./chrome.dmg', b'_' * 23963192),
            file_size=23963192)
        obj.save()

        response = self.client.get(reverse('sparkle_appcast', args=(app.name, channel.name)),
                                   HTTP_HOST='example.com')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_sparkle_with_minimum_system_version)

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

    @freeze_time('2014-10-14 08:28:05')
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_sparkle_critical(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='chrome')
        channel = ChannelFactory.create(name='stable')
        first_version = SparkleVersionFactory.create(
            app=app,
            channel=channel,
            version='782.110',
            short_version='13.0.782.110',
            file=SimpleUploadedFile('./chrome1.dmg', b'_' * 23963192),
            file_size=23963192)
        first_version.save()

        first_crit_version = SparkleVersionFactory.create(
            app=app,
            channel=channel,
            version='782.111',
            short_version='13.0.782.111',
            is_critical=True,
            file=SimpleUploadedFile('./chrome2.dmg', b'_' * 23963192),
            file_size=23963192)
        first_crit_version.save()

        last_version = SparkleVersionFactory.create(
            app=app,
            channel=channel,
            version='782.112',
            short_version='13.0.782.112',
            file=SimpleUploadedFile('./chrome3.dmg', b'_' * 23963192),
            file_size=23963192)
        last_version.save()

        second_crit_version = SparkleVersionFactory.create(
            app=app,
            channel=channel,
            version='782.113',
            short_version='13.0.782.113',
            is_critical=True,
            file=SimpleUploadedFile('./chrome4.dmg', b'_' * 23963192),
            file_size=23963192)
        second_crit_version.save()

        response = self.client.get("%s?appVersionShort=13.0.782.110" % reverse('sparkle_appcast', args=(app.name, channel.name)),
                                   HTTP_HOST='example.com')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.first_crit_response_sparkle)

        response = self.client.get("%s?appVersionShort=13.0.782.111" % reverse('sparkle_appcast', args=(app.name, channel.name)),
                                   HTTP_HOST='example.com')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.second_crit_response_sparkle)


    @freeze_time('2014-10-14 08:28:05')
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_sparkle_critical_on_other_channel(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='chrome')
        channel = ChannelFactory.create(name='stable')
        channel2 = ChannelFactory.create(name='beta')
        first_version = SparkleVersionFactory.create(
            app=app,
            channel=channel,
            version='782.110',
            short_version='13.0.782.110',
            file=SimpleUploadedFile('./chrome0.dmg', b'_' * 23963192),
            file_size=23963192)
        first_version.save()

        first_crit_version = SparkleVersionFactory.create(
            app=app,
            channel=channel2,
            version='782.111',
            short_version='13.0.782.111',
            is_critical=True,
            file=SimpleUploadedFile('./chrome2.dmg', b'_' * 23963192),
            file_size=23963192)
        first_crit_version.save()

        last_version = SparkleVersionFactory.create(
            app=app,
            channel=channel,
            version='782.112',
            short_version='13.0.782.112',
            file=SimpleUploadedFile('./chrome.dmg', b'_' * 23963192),
            file_size=23963192)
        last_version.save()

        response = self.client.get("%s?appVersionShort=13.0.782.111" % reverse('sparkle_appcast', args=(app.name, channel.name)),
                                   HTTP_HOST='example.com')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_sparkle)
