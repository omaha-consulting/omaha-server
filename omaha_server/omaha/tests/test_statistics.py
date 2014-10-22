# coding: utf8

from datetime import datetime

from django.test import TestCase

from mock import patch
from bitmapist import DayEvents

from omaha.statistics import userid_counting, add_app_statistics
from omaha.utils import redis, get_id


class StatisticsTest(TestCase):
    def setUp(self):
        redis.flushdb()

    def tearDown(self):
        redis.flushdb()

    @patch('omaha.statistics.add_app_statistics')
    def test_userid_counting(self, mock_add_app_statistics):
        now = datetime.utcnow()

        userid1 = '{F07B3878-CD6F-4B96-B52F-95C4D23077E0}'
        user1_id = get_id(userid1)

        userid2 = '{EC4C5647-F798-4BCA-83DA-926CD448A1D5}'
        user2_id = get_id(userid2)

        app_list = [dict(appid='{F97917B1-19AB-48C1-9802-CEF305B10804}'),
                    dict(appid='{555B8D18-076D-4576-9579-1FD7F0399EAE}')]

        request_events = DayEvents('request', now.year, now.month, now.day)

        self.assertFalse(user1_id in request_events)
        self.assertEqual(len(request_events), 0)

        userid_counting(userid1, app_list, 'win', 'stable')

        for app in app_list:
            mock_add_app_statistics.assert_any_call(user1_id, 'win', 'stable', app)

        self.assertEqual(len(request_events), 1)
        self.assertTrue(user1_id in request_events)

        userid_counting(userid1, app_list, 'win', 'stable')

        for app in app_list:
            mock_add_app_statistics.assert_any_call(user1_id, 'win', 'stable', app)

        self.assertEqual(len(request_events), 1)

        self.assertFalse(user2_id in request_events)
        userid_counting(userid2, app_list[:1], 'win', 'stable')
        self.assertTrue(user2_id in request_events)
        for app in app_list[:1]:
            mock_add_app_statistics.assert_any_call(user2_id, 'win', 'stable', app)

        self.assertEqual(len(request_events), 2)

    def test_add_app_statistics(self):
        now = datetime.utcnow()
        userid = 1
        channel = 'stable'
        platform = 'win'
        app = dict(appid='{F97917B1-20AB-48C1-9802-CEF305B10804}', version='30.0.123.1234')
        appid = app.get('appid')
        version = app.get('version')

        events_appid = DayEvents('request:%s' % app.get('appid'), now.year, now.month, now.day)
        events_appid_version = DayEvents('request:{}:{}'.format(appid, version), now.year, now.month, now.day)
        events_appid_platform =DayEvents('request:{}:{}'.format(appid, platform), now.year, now.month, now.day)
        events_appid_channel = DayEvents('request:{}:{}'.format(appid, channel), now.year, now.month, now.day)
        events_appid_platform_version = DayEvents('request:{}:{}:{}'.format(appid, platform, version), now.year, now.month, now.day)

        self.assertEqual(len(events_appid), 0)
        self.assertEqual(len(events_appid_version), 0)
        self.assertEqual(len(events_appid_platform), 0)
        self.assertEqual(len(events_appid_channel), 0)
        self.assertEqual(len(events_appid_platform_version), 0)

        add_app_statistics(userid, platform, channel, app)

        self.assertEqual(len(events_appid), 1)
        self.assertEqual(len(events_appid_version), 1)
        self.assertEqual(len(events_appid_platform), 1)
        self.assertEqual(len(events_appid_channel), 1)
        self.assertEqual(len(events_appid_platform_version), 1)

        self.assertIn(userid, events_appid)
        self.assertIn(userid, events_appid_version)
        self.assertIn(userid, events_appid_platform)
        self.assertIn(userid, events_appid_channel)
        self.assertIn(userid, events_appid_platform_version)
