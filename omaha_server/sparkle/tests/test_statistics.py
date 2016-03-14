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
from django.test import TestCase, RequestFactory

import mock
from django_redis import get_redis_connection
from bitmapist import DayEvents, HourEvents

from omaha.utils import get_id
from sparkle.statistics import update_live_statistics, collect_statistics
from omaha.statistics import add_app_statistics

redis = get_redis_connection('statistics')

class StatisticsTest(TestCase):
    request_factory = RequestFactory()

    def setUp(self):
        redis.flushdb()

    def tearDown(self):
        redis.flushdb()

    def test_add_app_statistics(self):
        userid1 = '{F07B3878-CD6F-4B96-B52F-95C4D23077E0}'
        user1_id = get_id(userid1)

        userid2 = '{EC4C5647-F798-4BCA-83DA-926CD448A1D5}'
        user2_id = get_id(userid2)

        appid = '{F97917B1-19AB-48C1-9802-CEF305B10804}'
        version = '0.0.0.1'
        channel = 'test'
        test_app = dict(appid=appid, version=version, tag=channel)

        install_app_events = DayEvents('new_install:%s' % appid)
        request_app_events = DayEvents('request:%s' % appid)
        request_version_events = DayEvents('request:{}:{}'.format(appid, version))
        install_platform_events = DayEvents('new_install:{}:{}'.format(appid, 'mac'))
        request_platform_events = DayEvents('request:{}:{}'.format(appid, 'mac'))
        request_channel_events = DayEvents('request:{}:{}'.format(appid, channel))
        request_platform_version_events = DayEvents('request:{}:{}:{}'.format(appid, 'mac', version))

        self.assertFalse(user1_id in install_app_events)
        self.assertEqual(len(install_app_events), 0)
        self.assertFalse(user1_id in install_platform_events)
        self.assertEqual(len(install_platform_events), 0)
        self.assertFalse(user1_id in request_app_events)
        self.assertEqual(len(request_app_events), 0)
        self.assertFalse(user1_id in request_platform_events)
        self.assertEqual(len(request_platform_events), 0)
        self.assertFalse(user1_id in request_version_events)
        self.assertEqual(len(request_version_events), 0)
        self.assertFalse(user1_id in request_channel_events)
        self.assertEqual(len(request_channel_events), 0)
        self.assertFalse(user1_id in request_platform_version_events)
        self.assertEqual(len(request_platform_version_events), 0)

        add_app_statistics(user1_id, 'mac', test_app)
        self.assertTrue(user1_id in install_app_events)
        self.assertEqual(len(install_app_events), 1)
        self.assertFalse(user1_id in request_app_events)
        self.assertEqual(len(request_app_events), 0)
        self.assertFalse(user1_id in request_platform_events)
        self.assertEqual(len(request_platform_events), 0)
        self.assertTrue(user1_id in request_version_events)
        self.assertEqual(len(request_version_events), 1)
        self.assertTrue(user1_id in install_platform_events)
        self.assertEqual(len(install_platform_events), 1)
        self.assertTrue(user1_id in request_channel_events)
        self.assertEqual(len(request_channel_events), 1)
        self.assertTrue(user1_id in request_platform_version_events)
        self.assertEqual(len(request_platform_version_events), 1)


        add_app_statistics(user2_id, 'mac', test_app)

        self.assertTrue(user2_id in install_app_events)
        self.assertEqual(len(install_app_events), 2)
        self.assertFalse(user2_id in request_app_events)
        self.assertEqual(len(request_app_events), 0)
        self.assertFalse(user2_id in request_platform_events)
        self.assertEqual(len(request_platform_events), 0)
        self.assertTrue(user2_id in request_version_events)
        self.assertEqual(len(request_version_events), 2)
        self.assertTrue(user2_id in install_platform_events)
        self.assertEqual(len(install_platform_events), 2)
        self.assertTrue(user2_id in request_channel_events)
        self.assertEqual(len(request_channel_events), 2)
        self.assertTrue(user2_id in request_platform_version_events)
        self.assertEqual(len(request_platform_version_events), 2)

        add_app_statistics(user1_id, 'mac', test_app)

        self.assertTrue(user1_id in install_app_events)
        self.assertEqual(len(install_app_events), 2)
        self.assertFalse(user1_id in request_app_events)
        self.assertEqual(len(request_app_events), 0)
        self.assertFalse(user1_id in request_platform_events)
        self.assertEqual(len(request_platform_events), 0)
        self.assertTrue(user1_id in request_version_events)
        self.assertEqual(len(request_version_events), 2)
        self.assertTrue(user1_id in install_platform_events)
        self.assertEqual(len(install_platform_events), 2)
        self.assertTrue(user1_id in request_channel_events)
        self.assertEqual(len(request_channel_events), 2)
        self.assertTrue(user1_id in request_platform_version_events)
        self.assertEqual(len(request_platform_version_events), 2)

    def test_update_live_statistics(self):
        userid1 = '{F07B3878-CD6F-4B96-B52F-95C4D23077E0}'
        user1_id = get_id(userid1)

        userid2 = '{EC4C5647-F798-4BCA-83DA-926CD448A1D5}'
        user2_id = get_id(userid2)

        appid = '{F97917B1-19AB-48C1-9802-CEF305B10804}'
        version = '0.0.0.1'

        request_version_events = HourEvents('online:{}:{}'.format(appid, version))
        request_platform_version_events = HourEvents('online:{}:{}:{}'.format(appid, 'mac', version))

        self.assertFalse(user1_id in request_version_events)
        self.assertEqual(len(request_version_events), 0)
        self.assertFalse(user1_id in request_platform_version_events)
        self.assertEqual(len(request_platform_version_events), 0)

        update_live_statistics(userid1, appid, version)

        self.assertTrue(user1_id in request_version_events)
        self.assertEqual(len(request_version_events), 1)
        self.assertTrue(user1_id in request_platform_version_events)
        self.assertEqual(len(request_platform_version_events), 1)

        update_live_statistics(userid1, appid, version)

        self.assertTrue(user1_id in request_version_events)
        self.assertEqual(len(request_version_events), 1)
        self.assertTrue(user1_id in request_platform_version_events)
        self.assertEqual(len(request_platform_version_events), 1)

        update_live_statistics(userid2, appid, version)

        self.assertTrue(user2_id in request_version_events)
        self.assertEqual(len(request_version_events), 2)
        self.assertTrue(user2_id in request_platform_version_events)
        self.assertEqual(len(request_platform_version_events), 2)

    @mock.patch('sparkle.statistics.update_live_statistics')
    def test_collect_statistics(self, mock_update_live_statistics):
        app_id = '00000000-0000-0000-0000-000000000001'
        app_name = "Sparrow"
        channel = "test"
        version = "0.0.0.1"
        deviceID = "A37152BF-A3CB-5FEC-8230-FACF43BDCDDD"
        request = RequestFactory().get('/sparkle/%s/%s/appcast.xml?appVersionShort=%s&deviceID=%s' %
                                       (app_name, channel, version, deviceID))

        collect_statistics(request, app_id, channel)

        mock_update_live_statistics.assert_called_with(deviceID, app_id, version)

