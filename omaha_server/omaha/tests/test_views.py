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

from datetime import datetime

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from xmlunittest import XmlTestMixin
from freezegun import freeze_time
from mock import patch
from bitmapist import DayEvents

import fixtures
from utils import temporary_media_root

from omaha.factories import ApplicationFactory, ChannelFactory, PlatformFactory, VersionFactory
from omaha.models import Action, EVENT_DICT_CHOICES, Data, NAME_DATA_DICT_CHOICES
from omaha.utils import redis, get_id


class UpdateViewTest(TestCase, XmlTestMixin):
    def setUp(self):
        self.client = Client()
        redis.flushdb()

    def tearDown(self):
        redis.flushdb()

    @freeze_time('2014-01-01 15:41:48')  # 56508 sec
    def test_updatecheck_negative(self):
        response = self.client.post(reverse('update'),
                                    fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_update_check_negative)

    @freeze_time('2014-01-01 15:41:48')  # 56508 sec
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_updatecheck_positive(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='chrome')
        platform = PlatformFactory.create(name='win')
        channel = ChannelFactory.create(name='stable')
        obj = VersionFactory.create(
            app=app,
            platform=platform,
            channel=channel,
            version='13.0.782.112',
            file=SimpleUploadedFile('./chrome_installer.exe', 'b' * 23963192),
            file_size=23963192)
        obj.file_hash = 'VXriGUVI0TNqfLlU02vBel4Q3Zo='
        obj.save()

        Action.objects.create(
            version=obj,
            arguments='--do-not-launch-chrome',
            event=EVENT_DICT_CHOICES['install'],
            run='chrome_installer.exe'
        )

        Action.objects.create(
            version=obj,
            event=EVENT_DICT_CHOICES['postinstall'],
            other=dict(
                version='13.0.782.112',
                onsuccess='exitsilentlyonlaunchcmd',
            )
        )

        response = self.client.post(reverse('update'),
                                    fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_update_check_positive)

    @freeze_time('2014-01-01 15:41:48')  # 56508 sec
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_userid_counting(self):
        now = datetime.utcnow()
        userid = '{D0BBD725-742D-44ae-8D46-0231E881D58E}'
        user_id = get_id(userid)
        appid1 = '{430FD4D0-B729-4F61-AA34-91526481799D}'
        appid2 = '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}'

        request_events = DayEvents('request', now.year, now.month, now.day)
        app1_events = DayEvents('request:%s' % appid1, now.year, now.month, now.day)
        app2_events = DayEvents('request:%s' % appid2, now.year, now.month, now.day)

        self.assertEqual(len(request_events), 0)
        self.assertEqual(len(app1_events), 0)
        self.assertEqual(len(app2_events), 0)


        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='chrome')
        platform = PlatformFactory.create(name='win')
        channel = ChannelFactory.create(name='stable')
        obj = VersionFactory.create(
            app=app,
            platform=platform,
            channel=channel,
            version='13.0.782.112',
            file=SimpleUploadedFile('./chrome_installer.exe', 'b' * 23963192))
        obj.file_hash = 'VXriGUVI0TNqfLlU02vBel4Q3Zo='
        obj.save()

        Action.objects.create(
            version=obj,
            arguments='--do-not-launch-chrome',
            event=EVENT_DICT_CHOICES['install'],
            run='chrome_installer.exe'
        )

        Action.objects.create(
            version=obj,
            event=EVENT_DICT_CHOICES['postinstall'],
            other=dict(
                version='13.0.782.112',
                onsuccess='exitsilentlyonlaunchcmd',
            )
        )

        self.client.post(reverse('update'),
                         fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(len(request_events), 1)
        self.assertEqual(len(app1_events), 1)
        self.assertEqual(len(app2_events), 1)
        self.assertTrue(user_id in request_events)
        self.assertTrue(user_id in app1_events)
        self.assertTrue(user_id in app2_events)

    @freeze_time('2014-01-01 15:45:54')  # 56754 sec
    def test_event(self):
        response = self.client.post(reverse('update'),
                                    fixtures.request_event, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_event)

    @freeze_time('2014-01-01 15:45:54')  # 56754 sec
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_data(self):
        app = ApplicationFactory.create(id='{430FD4D0-B729-4F61-AA34-91526481799D}', name='chrome')
        platform = PlatformFactory.create(name='win')
        channel = ChannelFactory.create(name='stable')
        obj = VersionFactory.create(
            app=app,
            platform=platform,
            channel=channel,
            version='13.0.782.112',
            file=SimpleUploadedFile('./chrome_installer.exe', 'b' * 23963192),
            file_size=23963192)
        obj.file_hash = 'VXriGUVI0TNqfLlU02vBel4Q3Zo='
        obj.save()

        Data.objects.create(
            version=obj,
            name=NAME_DATA_DICT_CHOICES['install'],
            index='verboselogging',
            value='app-specific values here')

        Data.objects.create(
            version=obj,
            name=NAME_DATA_DICT_CHOICES['untrusted'])

        response = self.client.post(reverse('update'),
                                    fixtures.request_data, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_data)

    def test_bad_request(self):
        response = self.client.post(reverse('update'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'bad request')


class SparkleViewTest(TestCase, XmlTestMixin):
    def setUp(self):
        self.client = Client()

    @freeze_time('2014-10-14 08:28:05')
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_sparkle(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='chrome')
        platform = PlatformFactory.create(name='mac')
        channel = ChannelFactory.create(name='stable')
        obj = VersionFactory.create(
            app=app,
            platform=platform,
            channel=channel,
            version='13.0.782.112',
            file=SimpleUploadedFile('./chrome.dmg', 'b' * 23963192))
        obj.file_hash = 'VXriGUVI0TNqfLlU02vBel4Q3Zo='
        obj.save()

        response = self.client.get(reverse('sparkle_appcast', args=(app.name, channel.name)),
                                   HTTP_HOST='example.com')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_sparkle)

    @freeze_time('2014-10-14 08:28:05')
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_sparkle_with_dsa_signature(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C9C}', name='chrome_dsa')
        platform = PlatformFactory.create(name='mac')
        channel = ChannelFactory.create(name='stable')
        obj = VersionFactory.create(
            app=app,
            platform=platform,
            channel=channel,
            version='13.0.782.112',
            dsa_signature='MCwCFCdoW13VBGJWIfIklKxQVyetgxE7AhQTVuY9uQT0KOV1UEk21epBsGZMPg==',
            file=SimpleUploadedFile('./chrome.dmg', 'b' * 23963192))
        obj.file_hash = 'VXriGUVI0TNqfLlU02vBel4Q3Zo='
        obj.save()

        response = self.client.get(reverse('sparkle_appcast', args=(app.name, channel.name)),
                                   HTTP_HOST='example.com')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(fixtures.response_sparkle_with_dsa,
                                        response.content)
