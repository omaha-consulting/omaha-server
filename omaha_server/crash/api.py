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

from django.db.utils import IntegrityError

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response

from omaha.api import BaseView, StandardResultsSetPagination
from crash.serializers import SymbolsSerializer, CrashSerializer
from crash.models import Symbols, Crash


class SymbolsViewSet(BaseView):
    queryset = Symbols.objects.all().order_by('-id')
    serializer_class = SymbolsSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super(SymbolsViewSet, self).create(request, *args, **kwargs)
        except IntegrityError:
            res = {"message": "Duplicate symbol"}
            return Response(data=res, status=status.HTTP_409_CONFLICT)


class CrashViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = Crash.objects.all().order_by('-id')
    serializer_class = CrashSerializer
    pagination_class = StandardResultsSetPagination
