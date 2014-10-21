# coding: utf8

from datetime import datetime

from django.test import TestCase

from bitmapist import DayEvents

from omaha.statistics import userid_counting
from omaha.utils import redis, get_id


class StatisticsTest(TestCase):
    def setUp(self):
        redis.flushdb()

    def tearDown(self):
        redis.flushdb()

    def test_userid_counting(self):
        now = datetime.utcnow()

        userid1 = '{F07B3878-CD6F-4B96-B52F-95C4D23077E0}'
        user1_id = get_id(userid1)

        userid2 = '{EC4C5647-F798-4BCA-83DA-926CD448A1D5}'
        user2_id = get_id(userid2)

        app_id_list = ['{F97917B1-19AB-48C1-9802-CEF305B10804}',
                       '{555B8D18-076D-4576-9579-1FD7F0399EAE}']

        request_events = DayEvents('request', now.year, now.month, now.day)
        app1_event = DayEvents('request:%s' % app_id_list[0], now.year, now.month, now.day)
        app2_event = DayEvents('request:%s' % app_id_list[1], now.year, now.month, now.day)

        self.assertFalse(user1_id in request_events)
        self.assertEqual(len(request_events), 0)

        userid_counting(userid1, app_id_list)

        self.assertEqual(len(request_events), 1)
        self.assertEqual(len(app1_event), 1)
        self.assertEqual(len(app2_event), 1)
        self.assertTrue(user1_id in request_events)
        self.assertTrue(user1_id in app1_event)
        self.assertTrue(user1_id in app2_event)

        userid_counting(userid1, app_id_list)

        self.assertEqual(len(request_events), 1)
        self.assertEqual(len(app1_event), 1)
        self.assertEqual(len(app2_event), 1)

        self.assertFalse(user2_id in request_events)
        userid_counting(userid2, app_id_list[:1])
        self.assertTrue(user2_id in request_events)
        self.assertTrue(user2_id in app1_event)
        self.assertFalse(user2_id in app2_event)

        self.assertEqual(len(request_events), 2)
        self.assertEqual(len(app1_event), 2)
        self.assertEqual(len(app2_event), 1)
