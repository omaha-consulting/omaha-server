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

from rest_framework import viewsets
from rest_framework import mixins

from serializers import AppSerializer, PlatformSerializer, ChannelSerializer, VersionSerializer
from models import Application, Platform, Channel, Version


class BaseView(mixins.ListModelMixin, mixins.CreateModelMixin,
               mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
               viewsets.GenericViewSet):
    pass


class AppViewSet(BaseView):
    """
    API endpoint that allows applications to be viewed.

    **Get applications list**:

    Example: ``GET http://example.com/api/app/``

    **Add application:**

    Example: ``POST http://example.com/api/app/``

        Content-Type: application/json
        {
            "id": "{8A76FC95-0086-4BCE-9517-DC09DDB5652F}",
            "name": "Chromium",
        }
    """
    queryset = Application.objects.all()
    serializer_class = AppSerializer


class PlatformViewSet(BaseView):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer


class VersionViewSet(BaseView):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
