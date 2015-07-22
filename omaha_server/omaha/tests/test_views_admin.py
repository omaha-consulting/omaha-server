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
from uuid import UUID

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

import mock
from pyquery import PyQuery as pq

from omaha_server.utils import is_private
from omaha.factories import ApplicationFactory, RequestFactory, AppRequestFactory
from omaha.models import Request, AppRequest
from omaha.forms import ManualCleanupForm
from omaha.views_admin import (
    StatisticsView,
    RequestListView,
)

User = get_user_model()


class AdminViewStatisticsTest(TestCase):
    def setUp(self):
        self.app1 = ApplicationFactory.create(name='app1', id='app1')
        self.app2 = ApplicationFactory.create(name='app2', id='app2')
        self.apps = [self.app1, self.app2]
        self.user = User.objects.create_superuser(
            username='test', email='test@example.com', password='test')

    @is_private()
    def test_statistics_view(self):
        view = StatisticsView()
        self.assertListEqual(list(view.get_queryset()), self.apps)


class ViewsStaffMemberRequiredTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.app = ApplicationFactory.create()
        self.request = Request.objects.create(version='1.0.0.0')
        self.app_request = AppRequest.objects.create(
            request=self.request,
            appid=self.app.id,
        )

    @is_private()
    def test_omaha_statistics(self):
        url = reverse('omaha_statistics')
        response = self.client.get(url)
        self.assertRedirects(response, '/admin/login/?next=%s' % url)

    @is_private()
    def test_omaha_statistics_detail(self):
        url = reverse('omaha_statistics_detail', kwargs=dict(name=self.app.name))
        response = self.client.get(url)
        self.assertRedirects(response, '/admin/login/?next=%s' % url)

    @is_private()
    def test_omaha_request_list(self):
        url = reverse('omaha_request_list', kwargs=dict(name=self.app.name))
        response = self.client.get(url)
        self.assertRedirects(response, '/admin/login/?next=%s' % url)

    @is_private()
    def test_omaha_request_detail(self):
        url = reverse('omaha_request_detail', kwargs=dict(pk=self.app_request.pk))
        response = self.client.get(url)
        self.assertRedirects(response, '/admin/login/?next=%s' % url)

    @is_private()
    def test_omaha_preferences(self):
        url = reverse('set_preferences', args=[''])
        response = self.client.get(url)
        self.assertRedirects(response, '/admin/login/?next=%s' % url)

    @is_private()
    def test_omaha_monitoring(self):
        url = reverse('monitoring')
        response = self.client.get(url)
        self.assertRedirects(response, '/admin/login/?next=%s' % url)


class AdminViewPreferencesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='test', email='test@example.com', password='test')
        self.client.login(username='test', password='test')

    @is_private()
    def test_set_timezone(self):
        url = reverse('set_preferences', args=['Timezone'])
        timezone = 'Asia/Omsk'
        self.client.post(url, dict(Timezone__timezone=timezone), follow=True)
        response = self.client.get(url)
        self.assertEqual(self.client.session["django_timezone"], timezone)
        self.assertContains(response, '<option value="Asia/Omsk" selected="selected">Asia/Omsk +0600</option>')


class FilteringAppRequestsByUserIdTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.app = ApplicationFactory.create(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C0}')
        self.userid1 = UUID(int=1)
        self.userid2 = UUID(int=2)
        self.app_req1 = AppRequestFactory(request=RequestFactory(userid=self.userid1))
        self.app_req2 = AppRequestFactory(request=RequestFactory(userid=self.userid1))
        self.app_req3 = AppRequestFactory(request=RequestFactory(userid=self.userid2))
        self.user = User.objects.create_superuser(
            username='test', email='test@example.com', password='test')
        self.client.login(username='test', password='test')

    @is_private()
    def test_filtering(self):
        url = reverse('omaha_request_list', kwargs=dict(name=self.app.name))
        data = {'request__userid': '',
                'request__created': '',
                'event_type': '',
                'event_result': ''}
        resp = self.client.get(url, data)
        d = pq(resp.content)
        res = d('#apprequest-table tbody tr')
        self.assertEqual(len(res), 3)
        data = {'request__userid': self.userid1,
                'request__created': '',
                'event_type': '',
                'event_result': ''}
        resp = self.client.get(url, data)
        d = pq(resp.content)
        res = d('#apprequest-table tbody tr')
        self.assertEqual(len(res), 2)


class ManualCleanupView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='test', email='test@example.com', password='test')
        self.client.login(username='test', password='test')

    @is_private()
    def test_limit_size_field(self):
        data = dict(limit_size=10)
        url = reverse('manual_cleanup', args=['feedback__Feedback'])
        with mock.patch('omaha.tasks.deferred_manual_cleanup.apply_async') as mocked:
            self.client.post(url, data=data)

        mock_args, mock_kwargs = mocked.call_args
        data.update(dict(limit_days=None))
        self.assertTrue(mocked.called)
        self.assertDictEqual(mock_args[1], data)

    @is_private()
    def test_limit_days_field(self):
        data = dict(limit_days=10)
        url = reverse('manual_cleanup', args=['feedback__Feedback'])
        with mock.patch('omaha.tasks.deferred_manual_cleanup.apply_async') as mocked:
            self.client.post(url, data=data)

        mock_args, mock_kwargs = mocked.call_args
        data.update(dict(limit_size=None))
        self.assertTrue(mocked.called)
        self.assertDictEqual(mock_args[1], data)

    @is_private()
    def test_all_fields(self):
        data = dict(limit_size=40, limit_days=5)
        url = reverse('manual_cleanup', args=['feedback__Feedback'])
        with mock.patch('omaha.tasks.deferred_manual_cleanup.apply_async') as mocked:
            self.client.post(url, data=data)

        mock_args, mock_kwargs = mocked.call_args
        self.assertTrue(mocked.called)
        self.assertDictEqual(mock_args[1], data)


class CrashManualCleanupView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='test', email='test@example.com', password='test')
        self.client.login(username='test', password='test')

    @is_private()
    def test_limit_duplictated_field(self):
        data = dict(limit_duplicated=10)
        url = reverse('manual_cleanup', args=['crash__Crash'])
        with mock.patch('omaha.tasks.deferred_manual_cleanup.apply_async') as mocked:
            self.client.post(url, data=data)

        mock_args, mock_kwargs = mocked.call_args
        data.update(dict(limit_size=None, limit_days=None))
        self.assertTrue(mocked.called)
        self.assertDictEqual(mock_args[1], data)

    @is_private()
    def test_all_fields(self):
        data = dict(limit_size=40, limit_days=5, limit_duplicated=73)
        url = reverse('manual_cleanup', args=['crash__Crash'])
        with mock.patch('omaha.tasks.deferred_manual_cleanup.apply_async') as mocked:
            self.client.post(url, data=data)

        mock_args, mock_kwargs = mocked.call_args
        self.assertTrue(mocked.called)
        self.assertDictEqual(mock_args[1], data)
