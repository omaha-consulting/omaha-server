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

from datetime import datetime

import mock
from django_redis import get_redis_connection
from bitmapist import DayEvents, HourEvents
from freezegun import freeze_time

from omaha.utils import get_id
from sparkle.statistics import update_live_statistics, collect_statistics
from sparkle.statistics import add_app_statistics

redis = get_redis_connection('statistics')


class StatisticsTest(TestCase):
    request_factory = RequestFactory()

    def setUp(self):
        redis.flushdb()

    def tearDown(self):
        redis.flushdb()

    @freeze_time('2016-1-1')
    def test_add_app_statistics(self):
        now = datetime.utcnow()
        next_month = now.replace(month=now.month + 1)
        userid = 1
        platform = 'mac'
        appid = '{F97917B1-19AB-48C1-9802-CEF305B10804}'
        version = '0.0.0.1'
        channel = 'test'
        test_app = dict(appid=appid, version=version, tag=channel)

        events_request_appid = lambda date=now: DayEvents.from_date('request:%s' % appid, date)
        events_new_appid = lambda date=now: DayEvents.from_date('new_install:%s' % appid, date)
        events_request_appid_version = lambda date=now: DayEvents.from_date('request:{}:{}'.format(appid, version),
                                                                            date)
        events_request_appid_platform = lambda date=now: DayEvents.from_date('request:{}:{}'.format(appid, platform),
                                                                             date)
        events_new_appid_platform = lambda date=now: DayEvents.from_date('new_install:{}:{}'.format(appid, platform),
                                                                         date)
        events_request_appid_channel = lambda date=now: DayEvents.from_date('request:{}:{}'.format(appid, channel),
                                                                            date)
        events_request_appid_platform_version = lambda date=now: DayEvents.from_date(
            'request:{}:{}:{}'.format(appid, platform, version), date)

        self.assertEqual(len(events_new_appid()), 0)
        self.assertEqual(len(events_request_appid()), 0)
        self.assertEqual(len(events_request_appid_version()), 0)
        self.assertEqual(len(events_request_appid_platform()), 0)
        self.assertEqual(len(events_new_appid_platform()), 0)
        self.assertEqual(len(events_request_appid_channel()), 0)
        self.assertEqual(len(events_request_appid_platform_version()), 0)

        add_app_statistics(userid, platform, test_app)
        self.assertEqual(len(events_new_appid()), 1)
        self.assertEqual(len(events_request_appid()), 0)
        self.assertEqual(len(events_request_appid_version()), 1)
        self.assertEqual(len(events_new_appid_platform()), 1)
        self.assertEqual(len(events_request_appid_platform()), 0)
        self.assertEqual(len(events_request_appid_channel()), 1)
        self.assertEqual(len(events_request_appid_platform_version()), 1)

        self.assertIn(userid, events_new_appid())
        self.assertIn(userid, events_request_appid_version())
        self.assertIn(userid, events_new_appid_platform())
        self.assertIn(userid, events_request_appid_channel())
        self.assertIn(userid, events_request_appid_platform_version())

        add_app_statistics(userid, platform, test_app)
        self.assertEqual(len(events_new_appid()), 1)
        self.assertEqual(len(events_request_appid()), 0)
        self.assertEqual(len(events_request_appid_version()), 1)
        self.assertEqual(len(events_new_appid_platform()), 1)
        self.assertEqual(len(events_request_appid_platform()), 0)
        self.assertEqual(len(events_request_appid_channel()), 1)
        self.assertEqual(len(events_request_appid_platform_version()), 1)

        with freeze_time(next_month):
            add_app_statistics(userid, platform, test_app)

        self.assertEqual(len(events_request_appid(next_month)), 1)
        self.assertEqual(len(events_request_appid_platform(next_month)), 1)
        self.assertEqual(len(events_new_appid(next_month)), 0)
        self.assertEqual(len(events_request_appid_version(next_month)), 1)
        self.assertEqual(len(events_new_appid_platform(next_month)), 0)
        self.assertEqual(len(events_request_appid_channel()), 1)
        self.assertEqual(len(events_request_appid_platform_version()), 1)

        self.assertIn(userid, events_request_appid(next_month))
        self.assertIn(userid, events_request_appid_platform(next_month))

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

