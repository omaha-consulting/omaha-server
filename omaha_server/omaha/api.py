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


from omaha.statistics import get_users_statistics_months, get_users_versions, get_channel_statistics
from omaha.serializers import (
    AppSerializer,
    DataSerializer,
    PlatformSerializer,
    ChannelSerializer,
    VersionSerializer,
    ActionSerializer,
    StatisticsMonthsSerializer,
    ServerVersionSerializer,
)
from omaha.models import (
    Application,
    Data,
    Platform,
    Channel,
    Version,
    Action,
    AppRequest,
)


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


class StatisticsMonthsListView(APIView):
    def get(self, request, format=None):
        data = get_users_statistics_months()
        serializer = StatisticsMonthsSerializer(dict(data=dict(data)))
        return Response(serializer.data)


class StatisticsMonthsDetailView(APIView):
    def get_object(self, name):
        try:
            return Application.objects.get(name=name)
        except Application.DoesNotExist:
            raise Http404

    def get(self, request, app_name, format=None):
        app = self.get_object(app_name)

        now = timezone.now()
        last_week = now - datetime.timedelta(days=7)

        qs = AppRequest.objects.filter(appid=app.id,
                                       request__created__range=[last_week, now])

        data = get_users_statistics_months(app_id=app.id)
        data.append(('install_count', qs.filter(events__eventtype=2).count()))
        data.append(('update_count', qs.filter(events__eventtype=3).count()))
        serializer = StatisticsMonthsSerializer(dict(data=dict(data)))
        return Response(serializer.data)


class StatisticsVersionsView(APIView):
    def get_object(self, name):
        try:
            return Application.objects.get(name=name)
        except Application.DoesNotExist:
            raise Http404

    def get(self, request, app_name, format=None):
        app = self.get_object(app_name)
        data = get_users_versions(app.id)
        serializer = StatisticsMonthsSerializer(dict(data=dict(data)))
        return Response(serializer.data)

class StatisticsChannelsView(APIView):
    def get_object(self, name):
        try:
            return Application.objects.get(name=name)
        except Application.DoesNotExist:
            raise Http404

    def get(self, request, app_name, format=None):
        app = self.get_object(app_name)
        data = get_channel_statistics(app.id)
        serializer = StatisticsMonthsSerializer(dict(data=dict(data)))
        return Response(serializer.data)


class ServerVersionView(APIView):
    def get(self, request, format=None):
        version = settings.APP_VERSION
        serializer = ServerVersionSerializer(dict(version=version))
        return Response(serializer.data)