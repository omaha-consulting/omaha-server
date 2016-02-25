# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2016 Crystalnix Limited

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
from collections import defaultdict
from django.conf import settings

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import pagination
from rest_framework.views import APIView
from rest_framework.response import Response

from omaha.api import BaseView
from omaha.models import Version
from sparkle.serializers import SparkleVersionSerializer
from sparkle.models import SparkleVersion


class LatestVersionView(APIView):
    """
    API returns an information about the latest versions of applications available on the server. The information contains supported platforms, provided channels, version numbers and download links.
    """
    permission_classes = []

    def get(self, request, format=None):
        win_versions = Version.objects.filter_by_enabled()\
            .select_related('app__name', 'channel__name')\
            .order_by('app__name', 'channel__name', '-version')\
            .distinct('app__name', 'channel__name')
        mac_versions = SparkleVersion.objects.filter_by_enabled()\
            .select_related('app__name', 'channel__name')\
            .order_by('app__name', 'channel__name', '-short_version')\
            .distinct('app__name', 'channel__name')

        recursive_dd = lambda: defaultdict(recursive_dd)
        data = recursive_dd()
        for v in win_versions:
            data[v.app.name]['win'][v.channel.name] = dict(version=str(v.version), url=v.file_absolute_url)
        for v in mac_versions:
            data[v.app.name]['mac'][v.channel.name] = dict(version=str(v.short_version), url=v.file_absolute_url)
        return Response(data)
