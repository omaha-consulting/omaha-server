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

import datetime

from django.http import Http404
from django.conf import settings
from django.utils import timezone

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import pagination
from rest_framework.views import APIView
from rest_framework.response import Response


from omaha.statistics import (
    get_users_statistics_months,
    get_users_versions,
    get_channel_statistics,
    get_users_live_versions
)
from omaha.serializers import (
    AppSerializer,
    DataSerializer,
    PlatformSerializer,
    ChannelSerializer,
    VersionSerializer,
    ActionSerializer,
    StatisticsMonthsSerializer,
    MonthRangeSerializer,
    MonthInputSerializer,
    ServerVersionSerializer,
    LiveStatisticsRangeSerializer,
)
from omaha.models import (
    Application,
    Data,
    Platform,
    Channel,
    Version,
    Action,
)
from omaha.utils import get_month_range_from_dict

class BaseView(mixins.ListModelMixin, mixins.CreateModelMixin,
               mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
               viewsets.GenericViewSet):
    pass


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class AppViewSet(BaseView):
    """
    API endpoint that allows applications to be viewed.

    ## Applications Collection

    ### List all Applications [GET]

    URL: `http://example.com/api/app/`

    Response:

        [
            {
                "id": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}",
                "name": "Chromium"
            },
            {
                "id": "{430FD4D0-B729-4F61-AA34-91526481799D}",
                "name": "Potato"
            }
        ]


    ### Create a Application [POST]

    URL: `http://example.com/api/app/`

    Headers:

        Content-Type: application/json

    Body:

        {
            "id": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}",
            "name": "Chromium",
        }

    Response:

        HTTP 201 CREATED
        Content-Type: application/json

        {
            "id": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}",
            "name": "Chromium",
        }

    ## Application

    ### Retrieve a Application [GET]

    URL: `http://example.com/api/app/[app_id]`

    Response:

        HTTP 201 CREATED
        Content-Type: application/json

        {
            "id": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}",
            "name": "Chromium",
        }

    ### Remove a Application [DELETE]

    URL: `http://example.com/api/app/[app_id]`

    Response:

        HTTP 204 NO CONTENT
        Content-Type: application/json
    """
    queryset = Application.objects.all().order_by('-id')
    serializer_class = AppSerializer


class DataViewSet(BaseView):
    queryset = Data.objects.all().order_by('-id')
    serializer_class = DataSerializer


class PlatformViewSet(BaseView):
    queryset = Platform.objects.all().order_by('-id')
    serializer_class = PlatformSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all().order_by('-id')
    serializer_class = ChannelSerializer


class VersionViewSet(BaseView):
    queryset = Version.objects.all().order_by('-id')
    serializer_class = VersionSerializer


class ActionViewSet(BaseView):
    queryset = Action.objects.all().order_by('-id')
    serializer_class = ActionSerializer


class StatisticsMonthsDetailView(APIView):
    def get_object(self, name):
        try:
            return Application.objects.get(name=name)
        except Application.DoesNotExist:
            raise Http404

    def get(self, request, app_name, format=None):
        app = self.get_object(app_name)
        dates = MonthRangeSerializer(data=request.GET)
        dates.is_valid()

        start, end = get_month_range_from_dict(dates.validated_data)

        diapasons = [((start.month if year == start.year else 1, end.month if year == end.year else 12), year)
                     for year in range(start.year, end.year+1)]

        win_data = dict(new=[], updates=[])
        mac_data = dict(new=[], updates=[])
        for diapason in diapasons:
            step = get_users_statistics_months(app_id=app.id, platform='win', year=diapason[1], start=diapason[0][0], end=diapason[0][1])
            win_data['new'] += step['new']
            win_data['updates'] += step['updates']
            step = get_users_statistics_months(app_id=app.id, platform='mac', year=diapason[1], start=diapason[0][0], end=diapason[0][1])
            mac_data['new'] += step['new']
            mac_data['updates'] += step['updates']

        serializer = StatisticsMonthsSerializer(dict(data=dict(win=win_data, mac=mac_data)))
        return Response(serializer.data)

class StatisticsVersionsView(APIView):
    def get_object(self, name):
        try:
            return Application.objects.get(name=name)
        except Application.DoesNotExist:
            raise Http404

    def get(self, request, app_name, format=None):
        now = timezone.now()
        app = self.get_object(app_name)

        date = MonthInputSerializer(data=request.GET)
        date.is_valid()
        date = date.validated_data.get('date', now)

        data = get_users_versions(app.id, date=date)
        serializer = StatisticsMonthsSerializer(dict(data=dict(data)))
        return Response(serializer.data)


class StatisticsVersionsLiveView(APIView):
    def get_object(self, name):
        try:
            return Application.objects.get(name=name)
        except Application.DoesNotExist:
            raise Http404

    def get(self, request, app_name, format=None):
        app = self.get_object(app_name)

        now = timezone.now()
        dates = LiveStatisticsRangeSerializer(data=request.GET)
        dates.is_valid()

        end = dates.validated_data.get('end', now)
        start = dates.validated_data.get('start', end - datetime.timedelta(hours=24))

        data = get_users_live_versions(app.id, start, end, tz=request.session.get('django_timezone', 'UTC'))
        serializer = StatisticsMonthsSerializer(dict(data=dict(data)))
        return Response(serializer.data)


class StatisticsChannelsView(APIView):
    def get_object(self, name):
        try:
            return Application.objects.get(name=name)
        except Application.DoesNotExist:
            raise Http404

    def get(self, request, app_name, format=None):
        now = timezone.now()
        app = self.get_object(app_name)

        date = MonthInputSerializer(data=request.GET)
        date.is_valid()
        date = date.validated_data.get('date', now)

        data = get_channel_statistics(app.id, date=date)
        serializer = StatisticsMonthsSerializer(dict(data=dict(data)))
        return Response(serializer.data)


class ServerVersionView(APIView):
    def get(self, request, format=None):
        version = settings.APP_VERSION
        serializer = ServerVersionSerializer(dict(version=version))
        return Response(serializer.data)