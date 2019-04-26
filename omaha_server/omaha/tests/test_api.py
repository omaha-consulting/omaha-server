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

from builtins import bytes, range

import base64
from datetime import datetime, timedelta, date
from uuid import UUID

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from lxml.builder import E
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from bitmapist import mark_event
from freezegun import freeze_time
import pytz
import factory

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
    PartialUpdateSerializer,
)
from omaha.factories import ApplicationFactory, DataFactory, PlatformFactory, ChannelFactory, VersionFactory, ActionFactory, PartialUpdateFactory
from omaha.models import Application, Data, Channel, Platform, Version, Action, PartialUpdate
from omaha.tests import fixtures, OverloadTestStorageMixin
from omaha.tests.utils import temporary_media_root, create_app_xml
from sparkle.models import SparkleVersion
from sparkle.statistics import userid_counting as mac_userid_counting
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    @is_private()
    def test_update(self):
        data = dict(id='test_id', name='test_name', data_set=[])
        response = self.client.post(reverse(self.url), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj_id = response.data['id']
        obj = Application.objects.get(id=obj_id)
        self.assertEqual(obj.name, 'test_name')
        url = reverse(self.url_detail, kwargs=dict(pk=obj_id))
        response = self.client.patch(url, dict(name='test_other_name'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj = Application.objects.get(id=obj_id)
        self.assertEqual(obj.name, 'test_other_name')


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

    @is_private()
    def test_update(self):
        app = ApplicationFactory.create()
        data = dict(name=0, app=app.pk)
        response = self.client.post(reverse(self.url), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj_id = response.data['id']
        obj = Data.objects.get(id=obj_id)
        self.assertEqual(obj.name, 0)
        url = reverse(self.url_detail, kwargs=dict(pk=obj_id))
        response = self.client.patch(url, dict(name=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj = Data.objects.get(id=obj_id)
        self.assertEqual(obj.name, 1)


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

    @is_private()
    def test_create(self):
        data = dict(name='test_name')
        response = self.client.post(reverse(self.url), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj_id = response.data['id']
        obj = Platform.objects.get(id=obj_id)
        self.assertEqual(obj.name, 'test_name')
        url = reverse(self.url_detail, kwargs=dict(pk=obj_id))
        response = self.client.patch(url, dict(name='test_name2'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj = Platform.objects.get(id=obj_id)
        self.assertEqual(obj.name, 'test_name2')


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

    @is_private()
    def test_update(self):
        data = dict(name='test_name')
        response = self.client.post(reverse(self.url), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj_id = response.data['id']
        obj = Channel.objects.get(id=obj_id)
        self.assertEqual(response.data, self.serializer(obj).data)
        url = reverse(self.url_detail, kwargs=dict(pk=obj_id))
        response = self.client.patch(url, dict(name='test_name2'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj = Channel.objects.get(id=obj_id)
        self.assertEqual(obj.name, 'test_name2')


class VersionTest(OverloadTestStorageMixin, BaseTest, APITestCase):
    url = 'version-list'
    url_detail = 'version-detail'
    factory = VersionFactory
    serializer = VersionSerializer
    model = Version

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def setUp(self):
        super(VersionTest, self).setUp()

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

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_update(self):
        data = dict(
            app=ApplicationFactory.create().id,
            platform=PlatformFactory.create().id,
            channel=ChannelFactory.create().id,
            version='1.2.3.4',
            file=SimpleUploadedFile("chrome.exe", b'content'),
            is_enabled=False,
        )
        response = self.client.post(reverse(self.url), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj_id = response.data['id']
        version = Version.objects.get(id=obj_id)
        self.assertEqual(version.file_size, len(b'content'))
        self.assertFalse(version.is_enabled)
        url = reverse(self.url_detail, kwargs=dict(pk=obj_id))
        response = self.client.patch(url, dict(is_enabled=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        version = Version.objects.get(id=obj_id)
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

    @is_private()
    def test_update(self):
        version = VersionFactory.create()
        data = dict(event=1, version=version.pk)
        response = self.client.post(reverse(self.url), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj_id = response.data['id']
        obj = Action.objects.get(id=obj_id)
        self.assertEqual(response.data, self.serializer(obj).data)
        url = reverse(self.url_detail, kwargs=dict(pk=obj_id))
        response = self.client.patch(url, dict(event=2))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj = Action.objects.get(id=obj_id)
        self.assertEqual(obj.event, 2)


class LiveStatistics(APITestCase):
    maxDiff = None

    def _generate_fake_statistics(self):
        date = datetime(2016, 2, 13, 0)
        for i in range(self.n_hours):
            for id in range(0, i):
                mark_event('request:app:win:2.0.0.0', id, now=date, track_hourly=True)
                mark_event('request:app:mac:4.0.0.1', id, now=date, track_hourly=True)
                mark_event('request:app:win:%s:2.0.0.0' % self.channel2.name,
                           id, now=date, track_hourly=True)
                mark_event('request:app:mac:%s:4.0.0.1' % self.channel2.name,
                           id, now=date, track_hourly=True)
            for id in range(i, self.n_hours):
                mark_event('request:app:win:1.0.0.0', id, now=date, track_hourly=True)
                mark_event('request:app:mac:3.0.0.0', id, now=date, track_hourly=True)
                mark_event('request:app:win:%s:1.0.0.0' % self.channel.name,
                           id, now=date, track_hourly=True)
                mark_event('request:app:mac:%s:3.0.0.0' % self.channel.name,
                           id, now=date, track_hourly=True)
            date += timedelta(hours=1)

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='secret', email='test@example.com')
        self.client.credentials(
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode(bytes('{}:{}'.format('test', 'secret'), 'utf8')).decode())

        redis.flushdb()
        self.app = Application.objects.create(id='app', name='app')
        self.channel = Channel.objects.create(name='stable')
        self.channel2 = Channel.objects.create(name='alpha')
        self.platform = Platform.objects.create(name='win')
        Platform.objects.create(name='mac')
        self.version1 = Version.objects.create(
            app=self.app,
            platform=self.platform,
            channel=self.channel,
            version='1.0.0.0',
            file=SimpleUploadedFile('./chrome_installer.exe', False))

        self.version2 = Version.objects.create(
            app=self.app,
            platform=self.platform,
            channel=self.channel2,
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
            channel=self.channel2,
            version='0.1',
            short_version='4.0.0.1',
            file=SimpleUploadedFile('./chrome_installer.dmg', False))

        self.n_hours = 36
        self._generate_fake_statistics()

        hours = [datetime(2016, 2, 13, 0, tzinfo=pytz.UTC) + timedelta(hours=hour)
                 for hour in range(self.n_hours)]
        self.win_statistics_ch1  = [('1.0.0.0', [[hour.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), self.n_hours - i]
                                            for (i, hour)in enumerate(hours)])]
        self.win_statistics_ch2 = [('2.0.0.0', [[hour.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), i]
                                                for (i, hour)in enumerate(hours)])]
        self.win_statistics = self.win_statistics_ch1 + self.win_statistics_ch2

        self.mac_statistics_ch1 = [('3.0.0.0', [[hour.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), self.n_hours - i]
                                            for (i, hour)in enumerate(hours)])]
        self.mac_statistics_ch2 = [('4.0.0.1', [[hour.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), i]
                                                for (i, hour)in enumerate(hours)])]
        self.mac_statistics = self.mac_statistics_ch1 + self.mac_statistics_ch2

        self.win_daily_stat_ch1 = [('1.0.0.0', [['2016-02-13T00:00:00.000000Z', 36], ['2016-02-14T00:00:00.000000Z', 12]])]
        self.win_daily_stat_ch2 = [('2.0.0.0', [['2016-02-13T00:00:00.000000Z', 23], ['2016-02-14T00:00:00.000000Z', 35]])]
        self.win_daily_statistics = self.win_daily_stat_ch1 + self.win_daily_stat_ch2

        self.mac_daily_stat_ch1 = [('3.0.0.0', [['2016-02-13T00:00:00.000000Z', 36], ['2016-02-14T00:00:00.000000Z', 12]])]
        self.mac_daily_stat_ch2 = [('4.0.0.1', [['2016-02-13T00:00:00.000000Z', 23], ['2016-02-14T00:00:00.000000Z', 35]])]
        self.mac_daily_statistics = self.mac_daily_stat_ch1 + self.mac_daily_stat_ch2

        self.data = {'hourly': {}, 'daily':{}}
        self.data['hourly']['channel1'] = dict(data=dict(win=dict(self.win_statistics_ch1),
                                             mac=dict(self.mac_statistics_ch1)))
        self.data['hourly']['channel2'] = dict(data=dict(win=dict(self.win_statistics_ch2),
                                             mac=dict(self.mac_statistics_ch2)))
        self.data['hourly']['all'] = dict(data=dict(win=dict(self.win_statistics),
                                             mac=dict(self.mac_statistics)))
        self.data['hourly']['channel1'] = dict(data=dict(win=dict(self.win_statistics_ch1),
                                                         mac=dict(self.mac_statistics_ch1)))
        self.data['daily']['channel1'] = dict(data=dict(win=dict(self.win_daily_stat_ch1),
                                             mac=dict(self.mac_daily_stat_ch1)))
        self.data['daily']['channel2'] = dict(data=dict(win=dict(self.win_daily_stat_ch2),
                                             mac=dict(self.mac_daily_stat_ch2)))
        self.data['daily']['all'] = dict(data=dict(win=dict(self.win_daily_statistics),
                                                            mac=dict(self.mac_daily_statistics)))

    @is_private()
    def test_unauthorized(self):
        client = APIClient()
        response = client.get(reverse('api-statistics-live', args=('app',)), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @freeze_time("2016-02-16")
    @is_private()
    def test_hourly_list(self):
        start = datetime(2016, 2, 13, 0)
        end = start + timedelta(hours=self.n_hours-1)
        response = self.client.get(reverse('api-statistics-live', args=('app',)),
                                   dict(start=start.isoformat(), end=end.isoformat()),
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(StatisticsMonthsSerializer(self.data['hourly']['all']).data, response.data)

        response = self.client.get(reverse('api-statistics-live', args=('app',)),
                                   dict(start=start.isoformat(), end=end.isoformat(), channel=self.channel.name),
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(StatisticsMonthsSerializer(self.data['hourly']['channel1']).data, response.data)

        response = self.client.get(reverse('api-statistics-live', args=('app',)),
                                   dict(start=start.isoformat(), end=end.isoformat(), channel=self.channel2.name),
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(StatisticsMonthsSerializer(self.data['hourly']['channel2']).data, response.data)

    @freeze_time("2016-03-16")
    @is_private()
    def test_daily_list(self):
        start = datetime(2016, 2, 13, 0)
        end = start + timedelta(hours=self.n_hours-1)
        response = self.client.get(reverse('api-statistics-live', args=('app',)),
                                   dict(start=start.isoformat(), end=end.isoformat()),
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(StatisticsMonthsSerializer(self.data['daily']['all']).data, response.data)

        response = self.client.get(reverse('api-statistics-live', args=('app',)),
                                   dict(start=start.isoformat(), end=end.isoformat(), channel=self.channel.name),
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(StatisticsMonthsSerializer(self.data['daily']['channel1']).data, response.data)

        response = self.client.get(reverse('api-statistics-live', args=('app',)),
                                   dict(start=start.isoformat(), end=end.isoformat(), channel=self.channel2.name),
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(StatisticsMonthsSerializer(self.data['daily']['channel2']).data, response.data)

class StatisticsMonthsMixin(object):
    url = None
    url_args = ()
    serializer = None
    url_get_params = None

    def _generate_fake_statistics(self):
        now = datetime.now()
        prev_year = now.year - 1

        for i in range(1, 13):
            date = datetime(year=prev_year, month=i, day=10)
            for id in range(1, i + 1):
                user_id = UUID(int=id)
                userid_counting(user_id, self.install_app_list, self.platform.name, now=date)
                user_id = UUID(int=1000 + id)
                mac_userid_counting(user_id, self.mac_app, 'mac', now=date)
            userid_counting(UUID(int=i), self.uninstall_app_list, self.platform.name, now=date)

        user_id = UUID(int=13)
        userid_counting(user_id, self.install_app_list, self.platform.name, now=datetime(year=now.year, month=1, day=1))
        userid_counting(user_id, self.uninstall_app_list, self.platform.name, now=datetime(year=now.year, month=1, day=1))
        user_id = UUID(int=1013)
        mac_userid_counting(user_id, self.mac_app, 'mac', now=datetime(year=now.year, month=1, day=1))

    @freeze_time("2016-01-27")
    @temporary_media_root()
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='secret', email='test@example.com')
        self.client.credentials(
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode(bytes('{}:{}'.format('test', 'secret'), 'utf8')).decode())

        redis.flushdb()
        self.app = Application.objects.create(id='app', name='app')
        self.channel = Channel.objects.create(name='stable')
        self.platform = Platform.objects.create(name='win')
        Platform.objects.create(name='mac')
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
        self.mac_version = SparkleVersion.objects.create(
            app=self.app,
            channel=self.channel,
            version='782.112',
            short_version='13.0.782.112',
            dsa_signature='MCwCFCdoW13VBGJWIfIklKxQVyetgxE7AhQTVuY9uQT0KOV1UEk21epBsGZMPg==',
            file=SimpleUploadedFile('./chrome.dmg', b'_' * 1024),
            file_size=1024)
        app_kwargs = dict(appid=self.app.id, version=str(self.version1.version))
        install_app = create_app_xml(events=[fixtures.event_install_success], **app_kwargs)
        uninstall_app = create_app_xml(events=[fixtures.event_uninstall_success], **app_kwargs)
        self.install_app_list = [install_app]
        self.uninstall_app_list = [uninstall_app]
        self.mac_app = dict(appid=self.app.id, version=str(self.mac_version.short_version))

        self._generate_fake_statistics()
        now = datetime.now()
        updates = [(datetime(now.year-1, x, 1).strftime("%Y-%m"), x - 1) for x in range(2, 13)]
        updates.append((datetime(now.year, 1, 1).strftime("%Y-%m"), 0))
        installs = [(datetime(now.year-1, x, 1).strftime("%Y-%m"), 1) for x in range(2, 13)]
        installs.append((datetime(now.year, 1, 1).strftime("%Y-%m"), 1))
        uninstalls = [(datetime(now.year-1, x, 1).strftime("%Y-%m"), 1) for x in range(2, 13)]
        uninstalls.append((datetime(now.year, 1, 1).strftime("%Y-%m"), 1))

        win_platform_statistics = dict(new=installs, updates=updates, uninstalls=uninstalls)
        mac_platform_statistics = dict(new=installs, updates=updates)
        self.users_statistics = dict(win=win_platform_statistics, mac=mac_platform_statistics)
        self.data = dict(data=dict(self.users_statistics))

    @is_private()
    def test_unauthorized(self):
        client = APIClient()
        response = client.get(reverse(self.url, args=self.url_args), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @is_private()
    def test_list(self):
        response = self.client.get(reverse(self.url, args=self.url_args), self.url_get_params, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.serializer(self.data).data, response.data)

    @freeze_time("2016-01-27")
    @is_private()
    def test_default_list(self):
        data_detail = self.data.copy()
        response = self.client.get(reverse(self.url, args=self.url_args), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.serializer(data_detail).data, response.data)


class StatisticsMonthsDetailTest(StatisticsMonthsMixin, APITestCase):
    url = 'api-statistics-months-detail'
    url_args = ('app',)
    serializer = StatisticsMonthsSerializer
    url_get_params = dict(start='2015-2', end='2016-1')

    @is_private()
    def test_list(self):
        data_detail = self.data.copy()
        response = self.client.get(reverse(self.url, args=self.url_args), self.url_get_params, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.serializer(data_detail).data, response.data)


class StatisticsVersionsTest(StatisticsMonthsMixin, APITestCase):
    url = 'api-statistics-versions'
    url_args = ('app',)
    serializer = StatisticsMonthsSerializer
    url_get_params = dict(date='2016-01')

    @freeze_time("2016-01-27")
    def setUp(self):
        super(StatisticsVersionsTest, self).setUp()
        data = get_users_versions(self.app.id)
        self.data = dict(data=dict(data))


class StatisticsChannelsTest(StatisticsMonthsMixin, APITestCase):
    url = 'api-statistics-channels'
    url_args = ('app',)
    serializer = StatisticsMonthsSerializer
    url_get_params = dict(date='2016-01')

    @freeze_time("2016-01-27")
    def setUp(self):
        super(StatisticsChannelsTest, self).setUp()
        data = get_channel_statistics(self.app.id)
        self.data = dict(data=dict(data))

    @is_private()
    def test_list(self):
        data_detail = self.data.copy()
        response = self.client.get(reverse(self.url, args=self.url_args), dict(date='2016-1'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.serializer(data_detail).data, response.data)


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



class PartialUpdateTest(BaseTest, APITestCase):
    url = 'partialupdate-list'
    url_detail = 'partialupdate-detail'
    factory = PartialUpdateFactory
    serializer = PartialUpdateSerializer

    @is_private()
    def test_create(self):
        version = VersionFactory.create()
        data = dict(
            is_enabled=True,
            exclude_new_users=True,
            version=version.pk,
            end_date=str(date.today()),
            percent=51.0,
            start_date=str(date.today()),
            active_users=1,
        )
        response = self.client.post(reverse(self.url), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = PartialUpdate.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(obj).data)

    @is_private()
    def test_update(self):
        version = VersionFactory.create()
        data = dict(
            is_enabled=True,
            exclude_new_users=True,
            version=version.pk,
            end_date=str(date.today()),
            percent=51.0,
            start_date=str(date.today()),
            active_users=1,
        )
        response = self.client.post(reverse(self.url), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj_id = response.data['id']
        obj = PartialUpdate.objects.get(id=obj_id)
        self.assertEqual(response.data, self.serializer(obj).data)
        url = reverse(self.url_detail, kwargs=dict(pk=obj_id))
        response = self.client.patch(url, dict(event=2))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj = PartialUpdate.objects.get(id=obj_id)
        self.assertEqual(obj.percent, 51.0)
