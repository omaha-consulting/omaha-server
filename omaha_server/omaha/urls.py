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

from django.conf import settings
from django.conf.urls import url

from omaha.views import UpdateView
from omaha.views_admin import (
    StatisticsView,
    StatisticsDetailView,
    LiveStatisticsView,
    VersionsUsageView,
    RequestListView,
    AppRequestDetailView,
    PreferenceFormView,
    MonitoringFormView,
    ManualCleanupFormView,
)


urlpatterns = [
    url(r'^service/update2$', UpdateView.as_view(), name='update'),
]


if settings.IS_PRIVATE:
    urlpatterns += [
        url(r'^admin/statistics/$', StatisticsView.as_view(), name='omaha_statistics'),
        url(r'^admin/statistics/(?P<name>[a-zA-Z0-9_ ]+)/$', StatisticsDetailView.as_view(),
            name='omaha_statistics_detail'),
        url(r'^admin/statistics/(?P<name>[a-zA-Z0-9_ ]+)/live/$', LiveStatisticsView.as_view(),
            name='omaha_live_statistics'),
        url(r'^admin/statistics/(?P<name>[a-zA-Z0-9_ ]+)/requests/$', RequestListView.as_view(), name='omaha_request_list'),
        url(r'^admin/statistics/(?P<name>[a-zA-Z0-9_ ]+)/usage/$', VersionsUsageView.as_view(), name='omaha_version_usage'),
        url(r'^admin/statistics/requests/(?P<pk>\d+)/$', AppRequestDetailView.as_view(), name='omaha_request_detail'),
        url(r'^admin/preferences/(?P<section>[a-zA-Z0-9_ ]*)', PreferenceFormView.as_view(), name='set_preferences'),
        url(r'^admin/monitoring/', MonitoringFormView.as_view(), name='monitoring'),
        url(r'^admin/manual_cleanup/(?P<model>[a-zA-Z0-9_ ]*)', ManualCleanupFormView.as_view(), name='manual_cleanup'),
    ]
