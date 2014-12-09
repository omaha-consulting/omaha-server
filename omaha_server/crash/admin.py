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

from django.contrib import admin

from crash.forms import SymbolsAdminForm
from models import Crash, Symbols


@admin.register(Crash)
class CrashAdmin(admin.ModelAdmin):
    list_display = ('app_id', 'user_id', 'created', 'modified',)
    list_display_links = ('app_id', 'user_id', 'created', 'modified',)
    list_filter = ('created',)
    search_fields = ('app_id', 'user_id',)


@admin.register(Symbols)
class SymbolsAdmin(admin.ModelAdmin):
    list_display = ('version',)
    list_display_links = ('version',)
    form = SymbolsAdminForm
