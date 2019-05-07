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

from django.utils import timezone
from datetime import datetime, timedelta
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
    is_user_active,
    get_kwargs_for_model,
    parse_os,
    parse_hw,
    parse_req,
    parse_apps,
    parse_events,
    collect_statistics,
    get_users_statistics_months,
    get_channel_statistics,
    get_users_versions,
    get_users_live_versions,
)

from omaha.tests.utils import temporary_media_root, create_app_xml
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
from sparkle.models import SparkleVersion
from sparkle.statistics import userid_counting as mac_userid_counting


class StatisticsTest(TestCase):
    def setUp(self):
        redis.flushdb()

    def tearDown(self):
        redis.flushdb()

    def generate_version(self, is_enabled):
        app = Application.objects.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', name='app')
        platform = Platform.objects.create(name='win')
        channel = Channel.objects.create(name='stable')
        userid = 1
        Version.objects.create(
            is_enabled=is_enabled,
            app=app,
            platform=platform,
            channel=channel,
            version='0.0.0.2',
            file=SimpleUploadedFile('./chrome_installer.exe', False))
        start = timezone.now() - timedelta(3)
        end = timezone.now()
        request = parse_request(fixtures.request_event_uninstall_success)
        apps = request.findall('app')
        userid_counting(userid, apps, platform)
        return get_users_live_versions(
            app_id=app.pk,
            channel=channel,
            start=start,
            end=end,
        )

    def test_get_live_statistics_with_enabled_version(self):
        data = self.generate_version(is_enabled=True)
        assert len(list(data['win'].keys())) == 1

    def test_get_live_statistics_with_disabled_version(self):
        data = self.generate_version(is_enabled=False)
        assert len(list(data['win'].keys())) == 1

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

    @freeze_time('2016-1-1')
    def test_add_app_statistics(self):
        now = datetime.utcnow()
        next_month = now.replace(month=now.month + 1)
        userid = 1
        channel = DEFAULT_CHANNEL
        platform = 'win'
        app_kwargs = dict(appid='{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}', nextversion='0.0.0.1')
        success_app = create_app_xml(events=fixtures.event_install_success, **app_kwargs)
        error_app = create_app_xml(events=fixtures.event_install_error, **app_kwargs)
        appid = app_kwargs.get('appid')
        version = app_kwargs.get('nextversion')

        events_request_appid = lambda date=now: DayEvents.from_date('request:%s' % appid, date)
        events_new_appid = lambda date=now: DayEvents.from_date('new_install:%s' % appid, date)
        events_request_appid_version = lambda date=now: DayEvents.from_date('request:{}:{}'.format(appid, version), date)
        events_request_appid_platform = lambda date=now: DayEvents.from_date('request:{}:{}'.format(appid, platform), date)
        events_new_appid_platform = lambda date=now: DayEvents.from_date('new_install:{}:{}'.format(appid, platform), date)
        events_request_appid_channel = lambda date=now: DayEvents.from_date('request:{}:{}'.format(appid, channel), date)
        events_request_appid_platform_version = lambda date=now: DayEvents.from_date(
            'request:{}:{}:{}'.format(appid, platform, version), date)
        events_request_appid_platform_channel_version = lambda date=now: DayEvents.from_date(
            'request:{}:{}:{}:{}'.format(appid, platform, channel, version), date)

        self.assertEqual(len(events_new_appid()), 0)
        self.assertEqual(len(events_request_appid()), 0)
        self.assertEqual(len(events_request_appid_version()), 0)
        self.assertEqual(len(events_request_appid_platform()), 0)
        self.assertEqual(len(events_new_appid_platform()), 0)
        self.assertEqual(len(events_request_appid_channel()), 0)
        self.assertEqual(len(events_request_appid_platform_version()), 0)
        self.assertEqual(len(events_request_appid_platform_channel_version()), 0)

        add_app_statistics(userid, platform, error_app)

        self.assertEqual(len(events_new_appid()), 0)
        self.assertEqual(len(events_request_appid()), 0)
        self.assertEqual(len(events_request_appid_version()), 0)
        self.assertEqual(len(events_request_appid_platform()), 0)
        self.assertEqual(len(events_new_appid_platform()), 0)
        self.assertEqual(len(events_request_appid_channel()), 0)
        self.assertEqual(len(events_request_appid_platform_version()), 0)
        self.assertEqual(len(events_request_appid_platform_channel_version()), 0)

        add_app_statistics(userid, platform, success_app)
        self.assertEqual(len(events_new_appid()), 1)
        self.assertEqual(len(events_request_appid()), 0)
        self.assertEqual(len(events_request_appid_version()), 1)
        self.assertEqual(len(events_new_appid_platform()), 1)
        self.assertEqual(len(events_request_appid_platform()), 0)
        self.assertEqual(len(events_request_appid_channel()), 1)
        self.assertEqual(len(events_request_appid_platform_version()), 1)
        self.assertEqual(len(events_request_appid_platform_channel_version()), 1)

        self.assertIn(userid, events_new_appid())
        self.assertIn(userid, events_request_appid_version())
        self.assertIn(userid, events_new_appid_platform())
        self.assertIn(userid, events_request_appid_channel())
        self.assertIn(userid, events_request_appid_platform_version())
        self.assertIn(userid, events_request_appid_platform_channel_version())

        add_app_statistics(userid, platform, success_app)
        self.assertEqual(len(events_new_appid()), 1)
        self.assertEqual(len(events_request_appid()), 0)
        self.assertEqual(len(events_request_appid_version()), 1)
        self.assertEqual(len(events_new_appid_platform()), 1)
        self.assertEqual(len(events_request_appid_platform()), 0)
        self.assertEqual(len(events_request_appid_channel()), 1)
        self.assertEqual(len(events_request_appid_platform_version()), 1)

        with freeze_time(next_month):
            add_app_statistics(userid, platform, error_app)

        self.assertEqual(len(events_request_appid(next_month)), 0)
        self.assertEqual(len(events_request_appid_platform(next_month)), 0)

        with freeze_time(next_month):
            add_app_statistics(userid, platform, success_app)

        self.assertEqual(len(events_request_appid(next_month)), 1)
        self.assertEqual(len(events_request_appid_platform(next_month)), 1)
        self.assertEqual(len(events_new_appid(next_month)), 0)
        self.assertEqual(len(events_request_appid_version(next_month)), 1)
        self.assertEqual(len(events_new_appid_platform(next_month)), 0)
        self.assertEqual(len(events_request_appid_channel(next_month)), 1)
        self.assertEqual(len(events_request_appid_platform_version(next_month)), 1)
        self.assertEqual(len(events_request_appid_platform_channel_version(next_month)), 1)

        self.assertIn(userid, events_request_appid(next_month))
        self.assertIn(userid, events_request_appid_platform(next_month))

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
        self.assertEqual(req.version, Request._meta.get_field('version').to_python('1.3.23.0'))
        self.assertEqual(req.ismachine, 1)
        self.assertEqual(req.sessionid, '{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}')
        self.assertEqual(req.userid, '{D0BBD725-742D-44ae-8D46-0231E881D58E}')
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
        self.assertEqual(app.nextversion, Request._meta.get_field('version').to_python('13.0.782.112'))
        self.assertEqual(app.lang, 'en')
        self.assertEqual(app.tag, 'stable')
        self.assertEqual(app.installage, 6)
        self.assertEqual(app.appid, '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}')

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

        self.assertEqual(req.version, Request._meta.get_field('version').to_python('1.3.23.0'))
        self.assertEqual(req.ismachine, 1)
        self.assertEqual(req.sessionid, '{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}')
        self.assertEqual(req.userid, '{D0BBD725-742D-44ae-8D46-0231E881D58E}')
        self.assertEqual(req.originurl, None)
        self.assertEqual(req.testsource, 'ossdev')
        self.assertEqual(req.updaterchannel, None)
        self.assertEqual(req.os, os)
        self.assertEqual(req.hw, None)

        self.assertEqual(app_req.version, None)
        self.assertEqual(app_req.nextversion, Request._meta.get_field('version').to_python('13.0.782.112'))
        self.assertEqual(app_req.lang, 'en')
        self.assertEqual(app_req.tag, 'stable')
        self.assertEqual(app_req.installage, 6)
        self.assertEqual(app_req.appid, '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}')
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

    def test_live_statistics_install(self):
        request = parse_request(fixtures.request_event_install_success)
        apps = request.findall('app')
        app = apps[0]
        channel = DEFAULT_CHANNEL
        now = datetime.utcnow()
        userid = 1
        platform = 'win'

        appid = app.get('appid')
        version_1 = '0.0.0.1'
        version_2 = '0.0.0.2'
        events_appid_version = lambda version: HourEvents('request:{}:{}'.format(appid, version), now.year, now.month, now.day, now.hour)
        events_appid_platform_version = lambda version: HourEvents('request:{}:{}:{}'.format(appid, platform, version), now.year, now.month, now.day, now.hour)
        events_appid_platform_channel_version = lambda version: HourEvents(
            'request:{}:{}:{}:{}'.format(appid, platform, channel, version), now.year, now.month, now.day, now.hour)

        self.assertEqual(len(events_appid_version(version_1)), 0)
        self.assertEqual(len(events_appid_platform_version(version_1)), 0)
        self.assertEqual(len(events_appid_platform_channel_version(version_1)), 0)
        userid_counting(userid, apps, platform)
        self.assertEqual(len(events_appid_version(version_1)), 1)
        self.assertEqual(len(events_appid_platform_version(version_1)), 1)
        self.assertEqual(len(events_appid_platform_channel_version(version_1)), 1)

        request = parse_request(fixtures.request_event_update_success)
        apps = request.findall('app')

        userid_counting(userid, apps, platform)

        self.assertEqual(len(events_appid_version(version_1)), 0)
        self.assertEqual(len(events_appid_platform_version(version_1)), 0)
        self.assertEqual(len(events_appid_platform_channel_version(version_1)), 0)
        self.assertEqual(len(events_appid_version(version_2)), 1)
        self.assertEqual(len(events_appid_platform_version(version_2)), 1)
        self.assertEqual(len(events_appid_platform_channel_version(version_2)), 1)

        request = parse_request(fixtures.request_event_uninstall_success)
        apps = request.findall('app')

        userid_counting(userid, apps, platform)

        self.assertEqual(len(events_appid_version(version_2)), 1)
        self.assertEqual(len(events_appid_platform_version(version_2)), 1)
        self.assertEqual(len(events_appid_platform_channel_version(version_2)), 1)

    def test_live_statistics_updatecheck(self):
        request = parse_request(fixtures.request_update_check)
        apps = request.findall('app')
        app = apps[0]
        channel = DEFAULT_CHANNEL
        now = datetime.utcnow()
        userid = 1
        platform = 'win'

        appid = app.get('appid')
        version = app.get('version')

        events_appid_version = HourEvents('request:{}:{}'.format(appid, version), now.year, now.month, now.day, now.hour)
        events_appid_platform_version = HourEvents('request:{}:{}:{}'.format(appid, platform, version), now.year, now.month, now.day, now.hour)
        events_appid_platform_channel_version = HourEvents(
            'request:{}:{}:{}:{}'.format(appid, platform, channel, version), now.year, now.month, now.day, now.hour)

        self.assertEqual(len(events_appid_version), 0)
        self.assertEqual(len(events_appid_platform_version), 0)
        self.assertEqual(len(events_appid_platform_channel_version), 0)

        userid_counting(userid, apps, platform)

        self.assertEqual(len(events_appid_version), 1)
        self.assertEqual(len(events_appid_platform_version), 1)
        self.assertEqual(len(events_appid_platform_channel_version), 1)


class GetStatisticsTest(TestCase):
    maxDiff = None

    def _generate_fake_statistics(self):
        now = datetime.now()
        year = now.year
        n_users = 12

        for i in range(1, n_users+1):
            date = datetime(year=year, month=i, day=10)
            for id in range(1, i + 1):
                user_id = UUID(int=id)
                userid_counting(user_id, self.install_app_list, self.platform.name, now=date)
                user_id = UUID(int=n_users + id)
                mac_userid_counting(user_id, self.mac_app, 'mac', now=date)
            userid_counting(UUID(int=i), self.uninstall_app_list, self.platform.name, now=date)


    @temporary_media_root()
    def setUp(self):
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
            file=SimpleUploadedFile('./chrome.dmg', b'_' * 23963192),
            file_size=23963192)

        app_kwargs = dict(appid=self.app.id, version=str(self.version1.version))
        install_app = create_app_xml(events=[fixtures.event_install_success], **app_kwargs)
        uninstall_app = create_app_xml(events=[fixtures.event_uninstall_success], **app_kwargs)
        self.install_app_list = [install_app]
        self.uninstall_app_list = [uninstall_app]
        self.mac_app = dict(appid=self.app.id, version=str(self.mac_version.short_version))

        self._generate_fake_statistics()
        now = datetime.now()
        win_updates = [(datetime(now.year, x, 1).strftime("%Y-%m"), x - 1) for x in range(1, 13)]
        win_installs = [(datetime(now.year, x, 1).strftime("%Y-%m"), 1) for x in range(1, 13)]
        uninstalls = [(datetime(now.year, x, 1).strftime("%Y-%m"), 1) for x in range(1, 13)]
        mac_updates = [(datetime(now.year, x, 1).strftime("%Y-%m"), x - 1) for x in range(1, 13)]
        mac_installs = [(datetime(now.year, x, 1).strftime("%Y-%m"), 1) for x in range(1, 13)]
        total_installs = list(map(lambda x, y: (x[0], x[1] + y[1]), win_installs, mac_installs))
        total_updates = list(map(lambda x, y: (x[0], x[1] + y[1]), win_updates, mac_updates))
        self.users_statistics = dict(new=total_installs, updates=total_updates, uninstalls=uninstalls)
        self.win_users_statistics = dict(new=win_installs, updates=win_updates, uninstalls=uninstalls)
        self.mac_users_statistics = dict(new=mac_installs, updates=mac_updates)


    def tearDown(self):
        redis.flushdb()

    def test_get_users_statistics_months(self):
        self.assertDictEqual(get_users_statistics_months(app_id=self.app.id), self.users_statistics)
        self.assertDictEqual(get_users_statistics_months(app_id=self.app.id, platform='win'), self.win_users_statistics)
        self.assertDictEqual(get_users_statistics_months(app_id=self.app.id, platform='mac'), self.mac_users_statistics)


    def test_get_chanels_statistics(self):
        now = datetime.now()
        with freeze_time(datetime(year=now.year, month=now.month, day=10)):
            self.assertListEqual(get_channel_statistics(self.app.id), [('stable', now.month*2)])

    def test_get_users_versions(self):
        now = datetime.now()
        expected = dict(win={'1.0.0.0': now.month}, mac={'13.0.782.112': now.month})
        with freeze_time(datetime(year=now.year, month=now.month, day=10)):
            self.assertDictEqual(get_users_versions(self.app.id), expected)
