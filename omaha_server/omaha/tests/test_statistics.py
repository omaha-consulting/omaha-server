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

from builtins import range

from datetime import datetime
from uuid import UUID

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from mock import patch
from freezegun import freeze_time
from bitmapist import DayEvents, HourEvents, mark_event

from omaha.tests import fixtures
from omaha.parser import parse_request
from omaha.statistics import (
    userid_counting,
    add_app_statistics,
    add_app_live_statistics,
    is_user_active,
    get_kwargs_for_model,
    parse_os,
    parse_hw,
    parse_req,
    parse_apps,
    parse_events,
    collect_statistics,
    update_live_statistics,
    get_users_statistics_months,
    get_users_statistics_weeks,
    get_channel_statistics,
    get_users_versions,
)

from omaha.tests.utils import temporary_media_root
from omaha.utils import redis, get_id
from omaha.settings import DEFAULT_CHANNEL
from omaha.models import (
    ACTIVE_USERS_DICT_CHOICES,
    Os,
    Hw,
    Request,
    AppRequest,
    Event,
    Application,
    Platform,
    Channel,
    Version,
)


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

        userid_counting(userid1, app_list, 'win')

        for app in app_list:
            mock_add_app_statistics.assert_any_call(user1_id, 'win', app, now=None)

        self.assertEqual(len(request_events), 1)
        self.assertTrue(user1_id in request_events)

        userid_counting(userid1, app_list, 'win')

        for app in app_list:
            mock_add_app_statistics.assert_any_call(user1_id, 'win', app, now=None)

        self.assertEqual(len(request_events), 1)

        self.assertFalse(user2_id in request_events)
        userid_counting(userid2, app_list[:1], 'win')
        self.assertTrue(user2_id in request_events)
        for app in app_list[:1]:
            mock_add_app_statistics.assert_any_call(user2_id, 'win', app, now=None)

        self.assertEqual(len(request_events), 2)

    def test_add_app_statistics(self):
        now = datetime.utcnow()
        userid = 1
        channel = DEFAULT_CHANNEL
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

        add_app_statistics(userid, platform, app)

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

    def test_add_app_live_statistics(self):
        request = parse_request(fixtures.request_update_check)
        app = request.findall('app')[0]

        now = datetime.utcnow()
        userid = 1
        platform = 'win'

        appid = app.get('appid')
        version = app.get('version')

        events_appid_version = HourEvents('online:{}:{}'.format(appid, version), now.year, now.month, now.day, now.hour)
        events_appid_platform_version = HourEvents('online:{}:{}:{}'.format(appid, platform, version), now.year, now.month, now.day, now.hour)

        self.assertEqual(len(events_appid_version), 0)
        self.assertEqual(len(events_appid_platform_version), 0)

        add_app_live_statistics(userid, platform, app)

        self.assertEqual(len(events_appid_version), 1)
        self.assertEqual(len(events_appid_platform_version), 1)

        self.assertIn(userid, events_appid_version)
        self.assertIn(userid, events_appid_platform_version)

    def test_is_user_active(self):
        userid = '{F07B3878-CD6F-4B96-B52F-95C4D23077E0}'
        id = get_id(userid)

        self.assertTrue(is_user_active(ACTIVE_USERS_DICT_CHOICES['all'], userid))
        self.assertFalse(is_user_active(ACTIVE_USERS_DICT_CHOICES['week'], userid))
        self.assertFalse(is_user_active(ACTIVE_USERS_DICT_CHOICES['month'], userid))

        mark_event('request', id)

        self.assertTrue(is_user_active(ACTIVE_USERS_DICT_CHOICES['all'], userid))
        self.assertTrue(is_user_active(ACTIVE_USERS_DICT_CHOICES['week'], userid))
        self.assertTrue(is_user_active(ACTIVE_USERS_DICT_CHOICES['month'], userid))

    def test_get_kwargs_for_model(self):
        os = dict(platform="win",
                  version="6.1",
                  sp="",
                  arch="x64")
        kwargs = get_kwargs_for_model(Os, os)
        self.assertDictEqual(kwargs, dict(platform="win",
                                          version="6.1",
                                          sp="",
                                          arch="x64",
                                          id=None))

    def test_parse_os(self):
        request = parse_request(fixtures.request_event)
        os = parse_os(request.os)
        self.assertIsInstance(os, Os)
        self.assertEqual(os.platform, 'win')
        self.assertEqual(os.version, '6.1')
        self.assertEqual(os.sp, '')
        self.assertEqual(os.arch, 'x64')

    def test_parse_hw(self):
        hw = dict(sse2="1")
        hw = parse_hw(hw)
        self.assertIsInstance(hw, Hw)
        self.assertEqual(hw.sse, None)
        self.assertEqual(hw.sse2, 1)
        self.assertEqual(hw.sse3, None)
        self.assertEqual(hw.ssse3, None)
        self.assertEqual(hw.sse41, None)
        self.assertEqual(hw.sse42, None)
        self.assertEqual(hw.avx, None)
        self.assertEqual(hw.physmemory, None)

    def test_parse_request(self):
        request = parse_request(fixtures.request_event)
        req = parse_req(request)
        self.assertIsInstance(req, Request)
        self.assertEqual(req.version, Request._meta.get_field_by_name('version')[0].to_python('1.3.23.0'))
        self.assertEqual(req.ismachine, 1)
        self.assertEqual(req.sessionid, '{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}')
        self.assertEqual(req.userid, '{F25EC606-5FC2-449b-91FF-FA21CADB46E4}')
        self.assertEqual(req.originurl, None)
        self.assertEqual(req.testsource, 'ossdev')
        self.assertEqual(req.updaterchannel, None)

    def test_parse_apps(self):
        request = parse_request(fixtures.request_event)
        req = parse_req(request)
        req.os = parse_os(request.os)
        req.hw = parse_hw(request.hw) if request.get('hw') else None
        req.save()

        apps = parse_apps(request.findall('app'), req)
        self.assertEqual(len(apps), 1)
        app = apps[0]
        self.assertIsInstance(app, AppRequest)
        self.assertEqual(app.version, None)
        self.assertEqual(app.nextversion, Request._meta.get_field_by_name('version')[0].to_python('13.0.782.112'))
        self.assertEqual(app.lang, 'en')
        self.assertEqual(app.tag, None)
        self.assertEqual(app.installage, 6)
        self.assertEqual(app.appid, '{8A69D345-D564-463C-AFF1-A69D9E530F96}')

    def test_parse_events(self):
        request = parse_request(fixtures.request_event)
        events = request.findall('app')[0].findall('event')
        events = parse_events(events)
        self.assertEqual(len(events), 3)
        event = events[0]
        self.assertIsInstance(event, Event)
        self.assertEqual(event.eventtype, 9)
        self.assertEqual(event.eventresult, 1)
        self.assertEqual(event.errorcode, 0)
        self.assertEqual(event.extracode1, 0)
        self.assertEqual(event.download_time_ms, None)
        self.assertEqual(event.downloaded, None)
        self.assertEqual(event.total, None)
        self.assertEqual(event.update_check_time_ms, None)
        self.assertEqual(event.install_time_ms, None)
        self.assertEqual(event.source_url_index, None)
        self.assertEqual(event.state_cancelled, None)
        self.assertEqual(event.time_since_update_available_ms, None)
        self.assertEqual(event.time_since_download_start_ms, None)
        self.assertEqual(event.nextversion, None)
        self.assertEqual(event.previousversion, None)

    def test_collect_statistics(self):
        request = parse_request(fixtures.request_event)

        self.assertEqual(Os.objects.all().count(), 0)
        self.assertEqual(Hw.objects.all().count(), 0)
        self.assertEqual(Request.objects.all().count(), 0)
        self.assertEqual(AppRequest.objects.all().count(), 0)
        self.assertEqual(Event.objects.all().count(), 0)

        collect_statistics(request)

        self.assertEqual(Os.objects.all().count(), 1)
        self.assertEqual(Hw.objects.all().count(), 0)
        self.assertEqual(Request.objects.all().count(), 1)
        self.assertEqual(AppRequest.objects.all().count(), 1)
        self.assertEqual(Event.objects.all().count(), 3)

        os = Os.objects.get()
        req = Request.objects.get()
        app_req = AppRequest.objects.get()
        events = Event.objects.all()

        self.assertEqual(os.platform, 'win')
        self.assertEqual(os.version, '6.1')
        self.assertEqual(os.sp, '')
        self.assertEqual(os.arch, 'x64')

        self.assertEqual(req.version, Request._meta.get_field_by_name('version')[0].to_python('1.3.23.0'))
        self.assertEqual(req.ismachine, 1)
        self.assertEqual(req.sessionid, '{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}')
        self.assertEqual(req.userid, '{F25EC606-5FC2-449b-91FF-FA21CADB46E4}')
        self.assertEqual(req.originurl, None)
        self.assertEqual(req.testsource, 'ossdev')
        self.assertEqual(req.updaterchannel, None)
        self.assertEqual(req.os, os)
        self.assertEqual(req.hw, None)

        self.assertEqual(app_req.version, None)
        self.assertEqual(app_req.nextversion, Request._meta.get_field_by_name('version')[0].to_python('13.0.782.112'))
        self.assertEqual(app_req.lang, 'en')
        self.assertEqual(app_req.tag, None)
        self.assertEqual(app_req.installage, 6)
        self.assertEqual(app_req.appid, '{8A69D345-D564-463C-AFF1-A69D9E530F96}')
        self.assertEqual(app_req.request, req)

        event = events[0]

        self.assertEqual(event.eventtype, 9)
        self.assertEqual(event.eventresult, 1)
        self.assertEqual(event.errorcode, 0)
        self.assertEqual(event.extracode1, 0)
        self.assertEqual(event.download_time_ms, None)
        self.assertEqual(event.downloaded, None)
        self.assertEqual(event.total, None)
        self.assertEqual(event.update_check_time_ms, None)
        self.assertEqual(event.install_time_ms, None)
        self.assertEqual(event.source_url_index, None)
        self.assertEqual(event.state_cancelled, None)
        self.assertEqual(event.time_since_update_available_ms, None)
        self.assertEqual(event.time_since_download_start_ms, None)
        self.assertEqual(event.nextversion, None)
        self.assertEqual(event.previousversion, None)

        for e in events:
            self.assertIn(e, app_req.events.all())

    def test_update_live_statistics_install(self):
        request = parse_request(fixtures.request_event_install_success)
        apps = request.findall('app')
        app = apps[0]

        now = datetime.utcnow()
        userid = 1
        platform = 'win'

        appid = app.get('appid')
        version_1 = '0.0.0.1'
        version_2 = '0.0.0.2'

        events_appid_version_1 = HourEvents('online:{}:{}'.format(appid, version_1), now.year, now.month, now.day, now.hour)
        events_appid_platform_version_1 = HourEvents('online:{}:{}:{}'.format(appid, platform, version_1), now.year, now.month, now.day, now.hour)

        self.assertEqual(len(events_appid_version_1), 0)
        self.assertEqual(len(events_appid_platform_version_1), 0)

        update_live_statistics(userid, apps, platform)

        self.assertEqual(len(events_appid_version_1), 1)
        self.assertEqual(len(events_appid_platform_version_1), 1)

        request = parse_request(fixtures.request_event_update_success)
        apps = request.findall('app')

        update_live_statistics(userid, apps, platform)

        events_appid_version_1 = HourEvents('online:{}:{}'.format(appid, version_1), now.year, now.month, now.day, now.hour)
        events_appid_platform_version_1 = HourEvents('online:{}:{}:{}'.format(appid, platform, version_1), now.year, now.month, now.day, now.hour)
        events_appid_version_2 = HourEvents('online:{}:{}'.format(appid, version_2), now.year, now.month, now.day, now.hour)
        events_appid_platform_version_2 = HourEvents('online:{}:{}:{}'.format(appid, platform, version_2), now.year, now.month, now.day, now.hour)

        self.assertEqual(len(events_appid_version_1), 0)
        self.assertEqual(len(events_appid_platform_version_1), 0)
        self.assertEqual(len(events_appid_version_2), 1)
        self.assertEqual(len(events_appid_platform_version_2), 1)

        request = parse_request(fixtures.request_event_uninstall_success)
        apps = request.findall('app')

        update_live_statistics(userid, apps, platform)

        events_appid_version_2 = HourEvents('online:{}:{}'.format(appid, version_2),
                                            now.year, now.month, now.day, now.hour)
        events_appid_platform_version_2 = HourEvents('online:{}:{}:{}'.format(appid, platform, version_2),
                                                     now.year, now.month, now.day, now.hour)

        self.assertEqual(len(events_appid_version_2), 0)
        self.assertEqual(len(events_appid_platform_version_2), 0)

    def test_update_live_statistics_updatecheck(self):
        request = parse_request(fixtures.request_update_check)
        apps = request.findall('app')
        app = apps[0]

        now = datetime.utcnow()
        userid = 1
        platform = 'win'

        appid = app.get('appid')
        version = app.get('version')

        events_appid_version = HourEvents('online:{}:{}'.format(appid, version), now.year, now.month, now.day, now.hour)
        events_appid_platform_version = HourEvents('online:{}:{}:{}'.format(appid, platform, version), now.year, now.month, now.day, now.hour)

        self.assertEqual(len(events_appid_version), 0)
        self.assertEqual(len(events_appid_platform_version), 0)

        update_live_statistics(userid, apps, platform)

        self.assertEqual(len(events_appid_version), 1)
        self.assertEqual(len(events_appid_platform_version), 1)


class GetStatisticsTest(TestCase):
    def _generate_fake_statistics(self):
        now = datetime.now()
        year = now.year

        for i in range(1, 13):
            date = datetime(year=year, month=i, day=10)
            for id in range(1, i + 1):
                user_id = UUID(int=id)
                userid_counting(user_id, self.app_list, self.platform.name, now=date)

    @temporary_media_root()
    def setUp(self):
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
        self.users_statistics = [(datetime(now.year, x, 1).strftime("%Y-%m"), x) for x in range(1, 13)]

    def tearDown(self):
        redis.flushdb()

    def test_get_users_statistics_months(self):
        self.assertListEqual(get_users_statistics_months(), self.users_statistics)
        self.assertListEqual(get_users_statistics_months(app_id=self.app.id), self.users_statistics)

    def test_get_users_statistics_weeks(self):
        now = datetime.now()
        with freeze_time(datetime(year=now.year, month=now.month, day=10)):
            self.assertListEqual(get_users_statistics_weeks(),
                                 [('Previous week', 0),
                                  ('Current week', now.month),
                                  ('Yesterday', 0),
                                  ('Today', now.month)])
            self.assertListEqual(get_users_statistics_weeks(self.app.id),
                                 [('Previous week', 0),
                                  ('Current week', now.month),
                                  ('Yesterday', 0),
                                  ('Today', now.month)])

    def test_get_chanels_statistics(self):
        now = datetime.now()
        with freeze_time(datetime(year=now.year, month=now.month, day=10)):
            self.assertListEqual(get_channel_statistics(self.app.id), [('stable', now.month)])

    def test_get_users_versions(self):
        now = datetime.now()
        with freeze_time(datetime(year=now.year, month=now.month, day=10)):
            self.assertListEqual(get_users_versions(self.app.id), [('1.0.0.0', now.month)])
