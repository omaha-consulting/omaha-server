# coding: utf8

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from xmlunittest import XmlTestMixin
from freezegun import freeze_time
from mock import patch

import fixtures
from utils import temporary_media_root

from omaha.factories import ApplicationFactory, ChannelFactory, PlatformFactory, VersionFactory
from omaha.models import Action, EVENT_DICT_CHOICES


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

        response = self.client.post(reverse('update'),
                                    fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_update_check_positive)

    @freeze_time('2014-01-01 15:45:54')  # 56754 sec
    def test_event(self):
        response = self.client.post(reverse('update'),
                                    fixtures.request_event, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_event)

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
