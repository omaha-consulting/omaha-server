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

from django.db.models.query import QuerySet
from django.db import models
from django.db.models import F, Sum

class CrashQuerySet(QuerySet):
    def filter_by_enabled(self, *args, **kwargs):
        return self.filter(is_enabled=True, *args, **kwargs)

    def get_size(self):
        return self.aggregate(size=Sum(F('archive_size') + F('minidump_size')))['size'] or 0

class CrashManager(models.Manager):
    def get_queryset(self):
        return CrashQuerySet(self.model, using=self._db)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError
        else:
            return getattr(self.get_queryset(), name)

class SymbolsQuerySet(QuerySet):
    def filter_by_enabled(self, *args, **kwargs):
        return self.filter(is_enabled=True, *args, **kwargs)

    def get_size(self):
        return self.aggregate(size=Sum('file_size'))['size'] or 0

class SymbolsManager(models.Manager):
    def get_queryset(self):
        return SymbolsQuerySet(self.model, using=self._db)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError
        else:
            return getattr(self.get_queryset(), name)
