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

from datetime import datetime
from unittest import TestCase

import django

from omaha.factories import (
    PlatformFactory, VersionFactory,
    ApplicationFactory,
)
from omaha.models import Version, Platform, Application
from omaha.settings import KEY_PREFIX, KEY_LAST_ID
from omaha.utils import (
    get_sec_since_midnight,
    redis,
    get_id,
    create_id,
    make_piechart,
    get_platforms_by_appid,
)
from sparkle.factories import SparkleVersionFactory
from sparkle.models import SparkleVersion

class UtilsTest(TestCase):
    def test_get_seconds_since_midnight(self):
        self.assertEqual(43,
                         get_sec_since_midnight(datetime(year=2014,
                                                         month=1,
                                                         day=1,
                                                         second=43)))

        self.assertEqual(0,
                         get_sec_since_midnight(datetime(year=2014,
                                                         month=1,
                                                         day=1)))

        self.assertEqual(3600,
                         get_sec_since_midnight(datetime(year=2014,
                                                         month=1,
                                                         day=1,
                                                         hour=1)))

        self.assertEqual(56508,
                         get_sec_since_midnight(datetime(year=2014,
                                                         month=1,
                                                         day=1,
                                                         hour=15,
                                                         minute=41,
                                                         second=48)))

        self.assertEqual((16 * 3600) + (23 * 60) + 17,
                         get_sec_since_midnight(datetime(year=2014,
                                                         month=1,
                                                         day=1,
                                                         hour=16,
                                                         minute=23,
                                                         second=17)))


class GetIdTest(TestCase):
    def setUp(self):
        self.uid = '{8C65E04C-0383-4AE2-893F-4EC7C58F70DC}'
        self.redis = redis
        self.redis.flushdb()

    def tearDown(self):
        self.redis.flushdb()

    def test_get_id_new(self):
        id = get_id(self.uid)

        self.assertIsInstance(id, int)

        _id = self.redis.get('{}:{}'.format(KEY_PREFIX, self.uid))
        self.assertEqual(id, int(_id))
        self.assertEqual(id, int(self.redis.get(KEY_LAST_ID)))

        get_id('new_uid')
        self.assertEqual(id + 1, int(self.redis.get(KEY_LAST_ID)))

    def test_get_id_exist(self):
        id = 123
        self.redis.set('{}:{}'.format(KEY_PREFIX, self.uid), 123)
        self.assertEqual(id, get_id(self.uid))

    def test_cteate_id(self):
        id = create_id(self.uid)

        self.assertIsInstance(id, int)

        _id = self.redis.get('{}:{}'.format(KEY_PREFIX, self.uid))
        self.assertEqual(id, int(_id))
        self.assertEqual(id, int(self.redis.get(KEY_LAST_ID)))


class ChartsTest(TestCase):
    def test_make_piechart(self):
        data = [('apple', 10), ('orange', 3)]
        self.assertDictEqual(make_piechart('test', data),
                             {'chartcontainer': 'chart_container_test',
                              'chartdata': {
                                  'extra1': {'tooltip': {'y_end': ' users', 'y_start': ''}},
                                  'x': ['apple', 'orange'],
                                  'y1': [10, 3]},
                              'charttype': 'pieChart',
                              'extra': {'jquery_on_ready': False,
                                        'tag_script_js': True,
                                        'x_axis_format': '',
                                        'x_is_date': False}})

class GetPlatformTest(django.test.TestCase):
    def setUp(self):
        self.app = ApplicationFactory()
        self.a_platform = PlatformFactory(name='a')
        self.b_platform = PlatformFactory(name='b')
        self.empty_platform = PlatformFactory(name='empty')
        self.mac_platform = PlatformFactory(name='mac')
        VersionFactory(platform=self.a_platform, app=self.app)
        VersionFactory(platform=self.b_platform, app=self.app)

    def test_without_mac_versions(self):
        self.assertEqual(Platform.objects.count(), 4)
        self.assertEqual(Version.objects.count(), 2)
        self.assertEqual(SparkleVersion.objects.filter(app=self.app).count(), 0)
        platforms = get_platforms_by_appid(self.app)
        self.assertEqual(len(platforms), 2)
        assert self.a_platform in platforms
        assert self.b_platform in platforms
        assert self.mac_platform not in platforms
        assert self.empty_platform not in platforms

    def test_with_mac_versions(self):
        self.assertEqual(Platform.objects.count(), 4)
        self.assertEqual(Version.objects.count(), 2)
        mac_version = SparkleVersionFactory(app=self.app)
        self.assertEqual(SparkleVersion.objects.filter(app=self.app).count(), 1)
        platforms = get_platforms_by_appid(self.app)
        self.assertEqual(len(platforms), 3)
        assert self.a_platform in platforms
        assert self.b_platform in platforms
        assert self.mac_platform in platforms
        assert self.empty_platform not in platforms