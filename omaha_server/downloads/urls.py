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

from django.conf.urls import url

from downloads.views import (
    AppListView,
    VersionListView,
    OmahaLatestVersionRedirectView,
    SparkleLatestVersionRedirectView,
)


urlpatterns = [
    url(r'^downloads/$', AppListView.as_view(), name='downloads'),
    url(r'^downloads/(?P<name>[a-zA-Z0-9_ ]+)/$', VersionListView.as_view(), name='downloads-app'),
    url(r'^downloads/latest/omaha/(?P<app>[a-zA-Z0-9_ ]+)/(?P<platform>[\w-]+)/(?P<channel>[\w-]+)/$',
        OmahaLatestVersionRedirectView.as_view(), name='downloads-latest-omaha'),
    url(r'^downloads/latest/sparkle/(?P<app>[a-zA-Z0-9_ ]+)/(?P<channel>[\w-]+)/$',
        SparkleLatestVersionRedirectView.as_view(), name='downloads-latest-sparkle'),
]
