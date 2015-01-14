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

import base64

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from omaha.serializers import AppSerializer, PlatformSerializer, ChannelSerializer, VersionSerializer
from omaha.factories import ApplicationFactory, PlatformFactory, ChannelFactory, VersionFactory
from omaha.models import Application, Channel, Platform, Version

from utils import temporary_media_root


User = get_user_model()


class BaseTest(object):
    url = None
    url_detail = None
    factory = None
    serializer = None
    maxDiff = None

    def setUp(self):
        self.objects = self.factory.create_batch(10)
        self.user = User.objects.create_user(username='test', password='secret', email='test@example.com')
        self.client.credentials(HTTP_AUTHORIZATION='Basic %s' % base64.b64encode('{}:{}'.format('test', 'secret')))

    def test_unauthorized(self):
        client = APIClient()
        response = client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        self.assertEqual(self.serializer(self.objects, many=True).data, response.data)

    def test_detail(self):
        obj = self.objects[0]
        url = reverse(self.url_detail, kwargs=dict(pk=obj.pk))

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, self.serializer(obj).data)


class AppTest(BaseTest, APITestCase):
    url = reverse('application-list')
    url_detail = 'application-detail'
    factory = ApplicationFactory
    serializer = AppSerializer

    def test_create(self):
        data = dict(id='test_id', name='test_name')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = Application.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(obj).data)


class PlatformTest(BaseTest, APITestCase):
    url = reverse('platform-list')
    url_detail = 'platform-detail'
    factory = PlatformFactory
    serializer = PlatformSerializer

    def test_create(self):
        data = dict(name='test_name')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = Platform.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(obj).data)


class ChannelTest(BaseTest, APITestCase):
    url = reverse('channel-list')
    url_detail = 'channel-detail'
    factory = ChannelFactory
    serializer = ChannelSerializer

    def test_create(self):
        data = dict(name='test_name')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = Channel.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(obj).data)


class VersionTest(BaseTest, APITestCase):
    url = reverse('version-list')
    url_detail = 'version-detail'
    factory = VersionFactory
    serializer = VersionSerializer

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_detail(self):
        super(VersionTest, self).test_detail()

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_list(self):
        super(VersionTest, self).test_list()

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_create(self):
        data = dict(
            app=ApplicationFactory.create().id,
            platform=PlatformFactory.create().id,
            channel=ChannelFactory.create().id,
            version='1.2.3.4',
            file=SimpleUploadedFile("chrome.exe", b'content'),
        )
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        version = Version.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(version).data)
        self.assertEqual(version.file_size, len(b'content'))
