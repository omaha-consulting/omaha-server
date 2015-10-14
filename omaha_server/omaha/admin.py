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
from omaha.models import Channel, Platform, Application, Version, Action, PartialUpdate, Data
from omaha.forms import ApplicationAdminForm, VersionAdminForm, ActionAdminForm, DataAdminForm
from dynamic_preferences.models import GlobalPreferenceModel, UserPreferenceModel

admin.site.unregister(GlobalPreferenceModel)
admin.site.unregister(UserPreferenceModel)

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name',)


class DataInline(admin.StackedInline):
    model = Data
    extra = 0
    form = DataAdminForm


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'id',)
    form = ApplicationAdminForm
    inlines = (DataInline,)


class ActionInline(admin.StackedInline):
    model = Action
    extra = 0
    form = ActionAdminForm


class PartialUpdateInline(admin.StackedInline):
    model = PartialUpdate
    extra = 0


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    inlines = (ActionInline, PartialUpdateInline,)
    list_display = ('created', 'modified', 'app', 'version', 'channel', 'platform', 'is_enabled')
    list_display_links = ('created', 'modified', 'version',)
    list_filter = ('channel__name', 'platform__name', 'app__name',)
    readonly_fields = ('file_hash',)
    form = VersionAdminForm
