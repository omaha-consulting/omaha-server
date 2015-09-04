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

from django.core.urlresolvers import resolve, reverse
from django.test import TestCase

from omaha_server.utils import is_private
from omaha.views import UpdateView
from omaha.views_admin import StatisticsView, StatisticsDetailView, RequestListView, AppRequestDetailView


class URLTestMixin(object):
    def assert_url_matches_view(self, view, expected_url, url_name,
                                url_args=None, url_kwargs=None, urlconf=None):
        """
        Assert a view's url is correctly configured
        Check the url_name reverses to give a correctly formated expected_url.
        Check the expected_url resolves to the expected view.
        """

        reversed_url = reverse(
            url_name,
            urlconf=urlconf,
            args=url_args,
            kwargs=url_kwargs,
        )
        self.assertEqual(reversed_url, expected_url)

        resolved_view = resolve(expected_url, urlconf=urlconf).func

        if hasattr(resolved_view, 'cls'):
            self.assertEqual(resolved_view.cls, view)
        else:
            self.assertEqual(resolved_view.__name__, view.__name__)


class Test(URLTestMixin, TestCase):
    def test_UpdateView(self):
        self.assert_url_matches_view(UpdateView, '/service/update2', 'update')

    @is_private()
    def test_StatisticsView(self):
        self.assert_url_matches_view(StatisticsView, '/admin/statistics/', 'omaha_statistics')

    @is_private()
    def test_StatisticsDetailView(self):
        self.assert_url_matches_view(StatisticsDetailView,
                                     '/admin/statistics/appName/',
                                     'omaha_statistics_detail',
                                     url_args=('appName',))

    @is_private()
    def test_RequestListView(self):
        self.assert_url_matches_view(RequestListView,
                                     '/admin/statistics/appName/requests/',
                                     'omaha_request_list',
                                     url_args=('appName',))

    @is_private()
    def test_AppRequestDetailView(self):
        self.assert_url_matches_view(AppRequestDetailView,
                                     '/admin/statistics/requests/123/',
                                     'omaha_request_detail',
                                     url_args=(123,))
