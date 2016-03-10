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
from datetime import datetime, timedelta
from uuid import UUID

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from bitmapist import mark_event
from freezegun import freeze_time
import pytz

from omaha_server.utils import is_private
from omaha.statistics import userid_counting, get_users_versions, get_channel_statistics
from omaha.utils import redis
from omaha.serializers import (
    AppSerializer,
    DataSerializer,
    PlatformSerializer,
    ChannelSerializer,
    VersionSerializer,
    ActionSerializer,
    StatisticsMonthsSerializer,
    ServerVersionSerializer,
)
from omaha.factories import ApplicationFactory, DataFactory, PlatformFactory, ChannelFactory, VersionFactory, ActionFactory
from omaha.models import Application, Data, Channel, Platform, Version, Action
from omaha.tests.utils import temporary_media_root
from sparkle.models import SparkleVersion

User = get_user_model()


class BaseTest(object):
    url = None
    url_args = ()
    url_detail = None
    factory = None
    serializer = None
    maxDiff = None
    is_private = True

    def _is_private(self):
        if not self.is_private and not settings.IS_PRIVATE:
            return True
        elif self.is_private and settings.IS_PRIVATE:
            return True
        else:
            return False

    def setUp(self):
        self.objects = self.factory.create_batch(10)
        self.user = User.objects.create_user(username='test', password='secret', email='test@example.com')
        self.client.credentials(
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode(bytes('{}:{}'.format('test', 'secret'), 'utf8')).decode())

    def test_unauthorized(self):
        if not self._is_private():
            return
        client = APIClient()
        response = client.get(reverse(self.url, args=self.url_args), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list(self):
        if not self._is_private():
            return
        response = self.client.get(reverse(self.url, args=self.url_args), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        self.assertEqual(self.serializer(self.objects, many=True).data, response.data[::-1])

    def test_detail(self):
        if not self._is_private():
            return
        obj = self.objects[0]
        url = reverse(self.url_detail, kwargs=dict(pk=obj.pk))

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, self.serializer(obj).data)


class AppTest(BaseTest, APITestCase):
    url = 'application-list'
    url_detail = 'application-detail'
    factory = ApplicationFactory
    serializer = AppSerializer

    @is_private()
    def test_create(self):
        data = dict(id='test_id', name='test_name', data_set=[])
        response = self.client.post(reverse(self.url
                                            ), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = Application.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(obj).data)


class DataTest(BaseTest, APITestCase):
    url = 'data-list'
    url_detail = 'data-detail'
    factory = DataFactory
    serializer = DataSerializer

    @is_private()
    def test_create(self):
        app = ApplicationFactory.create()
        data = dict(name=0, app=app.pk)
        response = self.client.post(reverse(self.url), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = Data.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(obj).data)


class PlatformTest(BaseTest, APITestCase):
    url = 'platform-list'
    url_detail = 'platform-detail'
    factory = PlatformFactory
    serializer = PlatformSerializer

    @is_private()
    def test_list(self):
        super(PlatformTest, self).test_list()

    @is_private()
    def test_create(self):
        data = dict(name='test_name')
        response = self.client.post(reverse(self.url), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = Platform.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(obj).data)


class ChannelTest(BaseTest, APITestCase):
    url = 'channel-list'
    url_detail = 'channel-detail'
    factory = ChannelFactory
    serializer = ChannelSerializer

    @is_private()
    def test_create(self):
        data = dict(name='test_name')
        response = self.client.post(reverse(self.url), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = Channel.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(obj).data)


class VersionTest(BaseTest, APITestCase):
    url = 'version-list'
    url_detail = 'version-detail'
    factory = VersionFactory
    serializer = VersionSerializer

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_detail(self):
        super(VersionTest, self).test_detail()

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_list(self):
        super(VersionTest, self).test_list()

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_create(self):
        data = dict(
            app=ApplicationFactory.create().id,
            platform=PlatformFactory.create().id,
            channel=ChannelFactory.create().id,
            version='1.2.3.4',
            file=SimpleUploadedFile("chrome.exe", b'content'),
        )
        response = self.client.post(reverse(self.url), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        version = Version.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(version).data)
        self.assertEqual(version.file_size, len(b'content'))
        self.assertTrue(version.is_enabled)


class ActionTest(BaseTest, APITestCase):
    url = 'action-list'
    url_detail = 'action-detail'
    factory = ActionFactory
    serializer = ActionSerializer

    @is_private()
    def test_create(self):
        version = VersionFactory.create()
        data = dict(event=1, version=version.pk)
        response = self.client.post(reverse(self.url), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = Action.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(obj).data)

class LiveStatistics(APITestCase):
    maxDiff = None

    def _generate_fake_statistics(self):
        # now = datetime(2016, 2, 13)
        date = datetime(2016, 2, 13, 0)
        for i in range(self.n_hours):
            for id in range(0, i):
                mark_event('online:app:win:2.0.0.0', id, now=date, track_hourly=True)
                mark_event('online:app:mac:4.0.0.1', id, now=date, track_hourly=True)
            for id in range(i, self.n_hours):
                mark_event('online:app:win:1.0.0.0', id, now=date, track_hourly=True)
                mark_event('online:app:mac:3.0.0.0', id, now=date, track_hourly=True)
            date += timedelta(hours=1)


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

        self.sparkle_version1 = SparkleVersion.objects.create(
            app=self.app,
            channel=self.channel,
            version='0.0',
            short_version='3.0.0.0',
            file=SimpleUploadedFile('./chrome_installer.dmg', False))

        self.sparkle_version2 = SparkleVersion.objects.create(
            app=self.app,
            channel=self.channel,
            version='0.1',
            short_version='4.0.0.1',
            file=SimpleUploadedFile('./chrome_installer.dmg', False))

        self.n_hours = 36
        self._generate_fake_statistics()

        hours = [datetime(2016, 2, 13, 0, tzinfo=pytz.UTC) + timedelta(hours=hour)
                 for hour in range(self.n_hours)]
        self.win_statistics = [('1.0.0.0', [[hour.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), self.n_hours - i]
                                            for (i, hour)in enumerate(hours)])]
        self.win_statistics.append(('2.0.0.0', [[hour.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), i]
                                                for (i, hour)in enumerate(hours)]))

        self.mac_statistics = [('3.0.0.0', [[hour.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), self.n_hours - i]
                                            for (i, hour)in enumerate(hours)])]
        self.mac_statistics.append(('4.0.0.1', [[hour.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), i]
                                                for (i, hour)in enumerate(hours)]))

        self.data = dict(data=dict(win=dict(self.win_statistics),
                                   mac=dict(self.mac_statistics)))

    @is_private()
    def test_unauthorized(self):
        client = APIClient()
        response = client.get(reverse('api-statistics-live', args=('app',)), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @is_private()
    def test_list(self):
        start = datetime(2016, 2, 13, 0)
        end = start + timedelta(hours=self.n_hours-1)
        response = self.client.get(reverse('api-statistics-live', args=('app',)),
                                   dict(start=start.isoformat(), end=end.isoformat()),
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(StatisticsMonthsSerializer(self.data).data, response.data)


@freeze_time("2016-01-27")
class StatisticsMonthsMixin(object):
    url = None
    url_args = ()
    serializer = None

    def _generate_fake_statistics(self):
        now = datetime.now()
        prev_year = now.year - 1

        for i in range(2, 13):
            date = datetime(year=prev_year, month=i, day=1)
            for id in range(1, i + 1):
                user_id = UUID(int=id)
                userid_counting(user_id, self.app_list, self.platform.name, now=date)

        user_id = UUID(int=13)
        userid_counting(user_id, self.app_list, self.platform.name, now=datetime(year=now.year, month=1, day=1))

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
        now = datetime.now()
        self.users_statistics = [(datetime(now.year-1, x, 1).strftime("%Y-%m"), x) for x in range(2, 13)]
        self.users_statistics.append((datetime(now.year, 1, 1).strftime("%Y-%m"), 1))
        self.data = dict(data=dict(self.users_statistics))

    @is_private()
    def test_unauthorized(self):
        client = APIClient()
        response = client.get(reverse(self.url, args=self.url_args), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    @is_private()
    def test_list(self):
        response = self.client.get(reverse(self.url, args=self.url_args), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.serializer(self.data).data, response.data)


class StatisticsMonthsListTest(StatisticsMonthsMixin, APITestCase):
    url = 'api-statistics-months-list'
    serializer = StatisticsMonthsSerializer

@freeze_time("2016-01-27")
class StatisticsMonthsDetailTest(StatisticsMonthsMixin, APITestCase):
    url = 'api-statistics-months-detail'
    url_args = ('app',)
    serializer = StatisticsMonthsSerializer

    @is_private()
    def test_list(self):
        data_detail = self.data.copy()
        data_detail['data']['install_count'] = 0
        data_detail['data']['update_count'] = 0
        response = self.client.get(reverse(self.url, args=self.url_args), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.serializer(data_detail).data, response.data)


class StatisticsVersionsTest(StatisticsMonthsMixin, APITestCase):
    url = 'api-statistics-versions'
    url_args = ('app',)
    serializer = StatisticsMonthsSerializer

    def setUp(self):
        super(StatisticsVersionsTest, self).setUp()
        data = get_users_versions(self.app.id)
        self.data = dict(data=dict(data))


class StatisticsChannelsTest(StatisticsMonthsMixin, APITestCase):
    url = 'api-statistics-channels'
    url_args = ('app',)
    serializer = StatisticsMonthsSerializer

    def setUp(self):
        super(StatisticsChannelsTest, self).setUp()
        data = get_channel_statistics(self.app.id)
        self.data = dict(data=dict(data))

class ServerVersionTest(APITestCase):
    url = 'api-version'
    serializer = ServerVersionSerializer

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='secret', email='test@example.com')
        self.client.credentials(
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode(bytes('{}:{}'.format('test', 'secret'), 'utf8')).decode())
        self.data = dict(version=settings.APP_VERSION)

    @is_private()
    def test(self):
        response = self.client.get(reverse(self.url), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.serializer(self.data).data, response.data)
