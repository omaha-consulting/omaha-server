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
from sparkle.models import SparkleVersion
from sparkle.forms import SparkleVersionAdminForm


@admin.register(SparkleVersion)
class VersionAdmin(admin.ModelAdmin):
    list_display = (
        'created', 'modified', 'app', 'version', 'short_version',
        'minimum_system_version', 'channel', 'is_enabled', 'is_critical'
    )
    list_display_links = ('created', 'modified', 'version',)
    list_filter = ('channel__name', 'app__name', 'is_enabled',)
    form = SparkleVersionAdminForm
