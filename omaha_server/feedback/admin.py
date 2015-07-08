# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2015 Crystalnix Limited

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

from crash.admin import TextInputFilter

from feedback.models import Feedback
from feedback.forms import FeedbackForm


class ScreenshotFilter(admin.SimpleListFilter):
    title = 'Screenshot'
    parameter_name = 'screenshot'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(screenshot='')
        if self.value() == 'no':
            return queryset.filter(screenshot='')

class BlackboxFilter(admin.SimpleListFilter):
    title = 'Blackbox'
    parameter_name = 'Blackbox'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(blackbox='')
        if self.value() == 'no':
            return queryset.filter(blackbox='')

class SystemLogsFilter(admin.SimpleListFilter):
    title = 'System Logs'
    parameter_name = 'system_logs'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(system_logs='')
        if self.value() == 'no':
            return queryset.filter(system_logs='')

class AttachedFileFilter(admin.SimpleListFilter):
    title = 'Attached File'
    parameter_name = 'attached_file'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(attached_file='')
        if self.value() == 'no':
            return queryset.filter(attached_file='')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'email', 'page_url')
    list_display_links = ('id', 'description')
    list_filter = (('id', TextInputFilter,), ScreenshotFilter, BlackboxFilter, SystemLogsFilter, AttachedFileFilter)
    form = FeedbackForm
