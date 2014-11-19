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
from django.contrib.auth import get_user_model


from omaha.factories import ApplicationFactory
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

