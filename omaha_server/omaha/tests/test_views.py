# coding: utf8

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from xmlunittest import XmlTestMixin
from freezegun import freeze_time

import fixtures
from utils import temporary_media_root

from omaha.factories import ApplicationFactory, ChannelFactory, PlatformFactory, VersionFactory


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
    def test_updatecheck_positive(self):
        app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='chrome')
        platform = PlatformFactory.create(name='win')
        channel = ChannelFactory.create(name='stable')
        VersionFactory.create(app=app,
                              platform=platform,
                              channel=channel,
                              version='13.0.782.112',
                              file=SimpleUploadedFile('./chrome_installer.exe', ''),
                              file_size=23963192,
                              file_hash='VXriGUVI0TNqfLlU02vBel4Q3Zo=')

        response = self.client.post(reverse('update'),
                                    fixtures.request_update_check, content_type='text/xml')

        self.assertEqual(response.status_code, 200)

        self.assertXmlDocument(response.content)
        self.assertXmlEquivalentOutputs(response.content,
                                        fixtures.response_update_check_positive)
