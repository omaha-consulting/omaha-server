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

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse


from omaha.factories import ApplicationFactory
from omaha.models import Request, AppRequest
from omaha.views_admin import (
    StatisticsView,
)


User = get_user_model()


class AdminViewStatisticsTest(TestCase):
    def setUp(self):
        self.app1 = ApplicationFactory.create(name='app1', id='app1')
        self.app2 = ApplicationFactory.create(name='app2', id='app2')
        self.apps = [self.app1, self.app2]
        self.user = User.objects.create_superuser(
            username='test', email='test@example.com', password='test')

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

    def test_omaha_statistics(self):
        url = reverse('omaha_statistics')
        response = self.client.get(url)
        self.assertRedirects(response, '/admin/login/?next=%s' % url)

    def test_omaha_statistics_detail(self):
        url = reverse('omaha_statistics_detail', kwargs=dict(name=self.app.name))
        response = self.client.get(url)
        self.assertRedirects(response, '/admin/login/?next=%s' % url)

    def test_omaha_request_list(self):
        url = reverse('omaha_request_list', kwargs=dict(name=self.app.name))
        response = self.client.get(url)
        self.assertRedirects(response, '/admin/login/?next=%s' % url)

    def test_omaha_request_detail(self):
        url = reverse('omaha_request_detail', kwargs=dict(pk=self.app_request.pk))
        response = self.client.get(url)
        self.assertRedirects(response, '/admin/login/?next=%s' % url)

    def test_omaha_set_timezone(self):
        url = reverse('set_timezone')
        response = self.client.get(url)
        self.assertRedirects(response, '/admin/login/?next=%s' % url)

class AdminViewTimezoneTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='test', email='test@example.com', password='test')
        self.client.login(username='test', password='test')

    def test_set_timezone(self):
        url = reverse('set_timezone')
        timezone = 'Asia/Omsk +0600'
        self.client.post(url, dict(timezone=timezone), follow=True)
        response = self.client.get(url)
        self.assertEqual(self.client.session["django_timezone"], timezone)
        self.assertContains(response, 'value="Asia/Omsk"')
