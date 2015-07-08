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
from django.core.exceptions import ObjectDoesNotExist

from celery import signature

from crash.forms import SymbolsAdminForm, CrashFrom
from crash.models import Crash, CrashDescription, Symbols
from crash.forms import TextInputForm


class BooleanFilter(admin.SimpleListFilter):
    title = None
    parameter_name = None

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        d = {self.parameter_name: ''}
        if self.value() == 'yes':
            return queryset.exclude(**d)
        if self.value() == 'no':
            return queryset.filter(**d)


class TextInputFilter(admin.filters.FieldListFilter):
    template = 'admin/textinput_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_equal = '%s' % field_path
        super(TextInputFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        self.form = self.get_form()

    def choices(self, cl):
        return []

    def expected_parameters(self):
        return [self.lookup_kwarg_equal]

    def get_form(self):
        return TextInputForm(data=self.used_parameters,
                             field_name=self.field_path)

    def queryset(self, request, queryset):
        if self.form.is_valid():
            filter_params = dict(filter(lambda x: bool(x[1]),
                                        self.form.cleaned_data.items()))
            return queryset.filter(**filter_params)
        else:
            return queryset


class CrashArchiveFilter(BooleanFilter):
    title = 'Instrumental file'
    parameter_name = 'archive'


@admin.register(CrashDescription)
class CrashDescriptionAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified')
    list_display = ('created', 'modified', 'summary')
    list_display_links = ('created', 'modified', 'summary')


class CrashDescriptionInline(admin.StackedInline):
    model = CrashDescription


@admin.register(Crash)
class CrashAdmin(admin.ModelAdmin):
    list_display = ('created', 'modified', 'archive_field', 'signature', 'appid', 'userid', 'summary_field')
    list_display_links = ('created', 'modified', 'signature', 'appid', 'userid',)
    list_filter = (('id', TextInputFilter,), 'created', CrashArchiveFilter)
    search_fields = ('appid', 'userid',)
    form = CrashFrom
    actions = ('regenerate_stacktrace',)
    inlines = [CrashDescriptionInline]

    def archive_field(self, obj):
        return bool(obj.archive)
    archive_field.short_description = 'Instrumental file'

    def summary_field(self, obj):
        try:
            return obj.crash_description.summary
        except ObjectDoesNotExist:
            return None
    summary_field.short_description = 'Summary'

    def regenerate_stacktrace(self, request, queryset):
        for i in queryset:
            signature("tasks.processing_crash_dump", args=(i.pk,)).apply_async(queue='default')
    regenerate_stacktrace.short_description = 'Regenerate stacktrace'



@admin.register(Symbols)
class SymbolsAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified', )
    list_display = ('created', 'modified', 'debug_file', 'debug_id',)
    list_display_links = ('created', 'modified', 'debug_file', 'debug_id',)
    form = SymbolsAdminForm

