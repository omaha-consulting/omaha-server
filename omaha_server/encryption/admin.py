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
import tarfile
import io

from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from encryption.models import GeneratedKey


if settings.ENABLE_BLACKBOX_ENCRYPTION:
    @admin.register(GeneratedKey)
    class GeneratedKeyAdmin(admin.ModelAdmin):
        list_display = ('id', 'type', 'created', 'is_enabled',)
        list_display_links = None
        actions = ('enable', 'disable', 'export')

        enable_change_view = False

        def change_view(self, request, object_id, form_url='', extra_context=None):
            return HttpResponseRedirect(reverse('admin:encryption_generatedkey_changelist'))

        def enable(self, request, queryset):
            queryset.update(is_enabled=True)
        enable.short_description = 'Enable keys'

        def disable(self, request, queryset):
            queryset.update(is_enabled=False)
        disable.short_description = 'Disable keys'

        def export(self, request, queryset):
            def add_file_to_tar(tarred, fileobj_str, filename):
                data = io.StringIO(fileobj_str)
                tarinfo = tarfile.TarInfo(filename)
                tarinfo.size = len(fileobj_str)
                tarred.addfile(tarinfo, fileobj=data)

            response = HttpResponse(content_type='application/x-gzip')
            response['Content-Disposition'] = 'attachment; filename=keys.tar.gz'
            tarred = tarfile.open(fileobj=response, mode='w')
            for key in queryset:
                add_file_to_tar(tarred, key.get_public_key(), '%s.pub' % key.id)
                add_file_to_tar(tarred, key.get_private_key(), '%s.key' % key.id)
            tarred.close()
            return response
        export.short_description = 'Export keys'


