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

from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.contrib import admin
from django.forms.widgets import TextInput
from celery import signature

from crash.forms import SymbolsAdminForm, CrashFrom
from crash.models import Crash, CrashDescription, Symbols


class TextInputForm(forms.Form):

    def __init__(self, *args, **kwargs):
        field_name = kwargs.pop('field_name')
        super(TextInputForm, self).__init__(*args, **kwargs)
        self.fields[field_name] = forms.CharField(
            widget=TextInput(attrs={'placeholder': 'Filter by ID'}),
            label='',
            required=False)

    def is_valid(self):
        valid = super(TextInputForm, self).is_valid()
        if not valid:
            return valid
        try:
            _id = self.cleaned_data['id']
            if _id != '':
                _ = int(_id)
        except ValueError:
            self.add_error('id', 'ID should be integer')
            return False
        return True


class TextInputFilter(admin.filters.FieldListFilter):
    template = 'admin/textinput_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_equal = '%s' % field_path
        super(TextInputFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        self.form = self.get_form(request)

    def choices(self, cl):
        return []

    def expected_parameters(self):
        return [self.lookup_kwarg_equal]

    def get_form(self, request):
        return TextInputForm(data=self.used_parameters,
                             field_name=self.field_path)

    def queryset(self, request, queryset):
        if self.form.is_valid():
            # get no null params
            filter_params = dict(filter(lambda x: bool(x[1]),
                                        self.form.cleaned_data.items()))
            return queryset.filter(**filter_params)
        else:
            return queryset


class CrashArchiveFilter(admin.SimpleListFilter):
    title = 'Instrumental file'
    parameter_name = 'instrumental_file'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(archive='')
        if self.value() == 'no':
            return queryset.filter(archive='')


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

