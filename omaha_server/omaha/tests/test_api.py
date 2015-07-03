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

from __future__ import unicode_literals
from builtins import bytes, range

import base64
from datetime import datetime
from uuid import UUID

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from omaha.statistics import userid_counting, get_users_versions, get_channel_statistics
from omaha.utils import redis

from omaha.serializers import (
    AppSerializer,
    PlatformSerializer,
    ChannelSerializer,
    VersionSerializer,
    ActionSerializer,
    StatisticsMonthsSerializer,
    ServerVersionSerializer,
)
from omaha.factories import ApplicationFactory, PlatformFactory, ChannelFactory, VersionFactory, ActionFactory
from omaha.models import Application, Channel, Platform, Version, Action

from omaha.tests.utils import temporary_media_root


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
        self.client.credentials(
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode(bytes('{}:{}'.format('test', 'secret'), 'utf8')).decode())

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
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        self.assertEqual(self.serializer(self.objects, many=True).data, response.data[::-1])

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


class ActionTest(BaseTest, APITestCase):
    url = reverse('action-list')
    url_detail = 'action-detail'
    factory = ActionFactory
    serializer = ActionSerializer

    def test_create(self):
        version = VersionFactory.create()
        data = dict(event=1, version=version.pk)
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = Action.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(obj).data)


class StatisticsMonthsMixin(object):
    url = None
    serializer = None

    def _generate_fake_statistics(self):
        now = datetime.now()
        year = now.year

        for i in range(1, 13):
            date = datetime(year=year, month=i, day=1)
            for id in range(1, i + 1):
                user_id = UUID(int=id)
                userid_counting(user_id, self.app_list, self.platform.name, now=date)

    @temporary_media_root()
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='secret', email='test@example.com')
        self.client.credentials(
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode(bytes('{}:{}'.format('test', 'secret'), 'utf8')).decode())

        redis.flushdb()
        self.app = Application.objects.create(id='app', name='app')
        self.channel = Channel.objects.create(name='stable')
        self.platform = Platform.objects.create(name='win')
        self.version1 = Version.objects.create(
            app=self.app,
            platform=self.platform,
            channel=self.channel,
            version='1.0.0.0',
            file=SimpleUploadedFile('./chrome_installer.exe', False))
        self.version2 = Version.objects.create(
            app=self.app,
            platform=self.platform,
            channel=self.channel,
            version='2.0.0.0',
            file=SimpleUploadedFile('./chrome_installer.exe', False))
        self.app_list = [dict(appid=self.app.id, version=str(self.version1.version))]

        self._generate_fake_statistics()
        self.users_statistics = [('January', 1),
                                 ('February', 2),
                                 ('March', 3),
                                 ('April', 4),
                                 ('May', 5),
                                 ('June', 6),
                                 ('July', 7),
                                 ('August', 8),
                                 ('September', 9),
                                 ('October', 10),
                                 ('November', 11),
                                 ('December', 12)]
        self.data = dict(data=dict(self.users_statistics))

    def test_unauthorized(self):
        client = APIClient()
        response = client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.serializer(self.data).data, response.data)


class StatisticsMonthsListTest(StatisticsMonthsMixin, APITestCase):
    url = reverse('api-statistics-months-list')
    serializer = StatisticsMonthsSerializer


class StatisticsMonthsDetailTest(StatisticsMonthsMixin, APITestCase):
    url = reverse('api-statistics-months-detail', args=('app',))
    serializer = StatisticsMonthsSerializer

    def test_list(self):
        data_detail = self.data.copy()
        data_detail['data']['install_count'] = 0
        data_detail['data']['update_count'] = 0
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.serializer(data_detail).data, response.data)


class StatisticsVersionsTest(StatisticsMonthsMixin, APITestCase):
    url = reverse('api-statistics-versions', args=('app',))
    serializer = StatisticsMonthsSerializer

    def setUp(self):
        super(StatisticsVersionsTest, self).setUp()
        data = get_users_versions(self.app.id)
        self.data = dict(data=dict(data))


class StatisticsChannelsTest(StatisticsMonthsMixin, APITestCase):
    url = reverse('api-statistics-channels', args=('app',))
    serializer = StatisticsMonthsSerializer

    def setUp(self):
        super(StatisticsChannelsTest, self).setUp()
        data = get_channel_statistics(self.app.id)
        self.data = dict(data=dict(data))

class ServerVersionTest(APITestCase):
    url = reverse('api-version')
    serializer = ServerVersionSerializer

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='secret', email='test@example.com')
        self.client.credentials(
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode(bytes('{}:{}'.format('test', 'secret'), 'utf8')).decode())
        self.data = dict(version=settings.APP_VERSION)

    def test(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.serializer(self.data).data, response.data)
