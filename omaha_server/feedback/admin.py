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

from crash.admin import TextInputFilter, BooleanFilter

from feedback.models import Feedback, FeedbackDescription
from feedback.forms import FeedbackForm


class ScreenshotFilter(BooleanFilter):
    title = 'Screenshot'
    parameter_name = 'screenshot'


class BlackboxFilter(BooleanFilter):
    title = 'Blackbox'
    parameter_name = 'blackbox'


class SystemLogsFilter(BooleanFilter):
    title = 'System Logs'
    parameter_name = 'system_logs'


class AttachedFileFilter(BooleanFilter):
    title = 'Attached File'
    parameter_name = 'attached_file'


def short_url(obj):
    limit = 60
    res = obj.page_url
    if res is None:
        return ""

    return res if len(res) < limit else res[:limit] + '...'
short_url.short_description = 'Page URL'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'email', short_url, 'created_at', 'ip',)
    list_display_links = ('id', 'description')
    list_filter = (('id', TextInputFilter,), ScreenshotFilter, BlackboxFilter, SystemLogsFilter, AttachedFileFilter, 'created_at',)
    form = FeedbackForm
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        qs = super(FeedbackAdmin, self).get_queryset(request)
        return qs.get_feedbacks()


@admin.register(FeedbackDescription)
class FeedbackDescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'email', short_url, 'created_at', 'ip',)
    list_display_links = ('id', 'description')
    list_filter = (('id', TextInputFilter,), ScreenshotFilter, BlackboxFilter, SystemLogsFilter, AttachedFileFilter, 'created_at')
    form = FeedbackForm
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        qs = super(FeedbackDescriptionAdmin, self).get_queryset(request)
        return qs.get_feedbacks_description()
