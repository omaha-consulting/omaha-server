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

import django_tables2 as tables
from django_tables2 import A

from omaha.models import AppRequest
from omaha.filters import EVENT_TYPE, EVENT_RESULT
from django.utils.html import format_html


def get_badge(event):
    name = EVENT_TYPE[event.eventtype]
    result = EVENT_RESULT[event.eventresult]
    badge = 'info'
    if 'success' in result:
        badge = 'success'
    if 'error' in result:
        badge = 'important'
    return '<p class="badge badge-%s">%s</p>' % (badge, name)


class EventsColumn(tables.Column):
    def render(self, record):
        res = map(get_badge, record.events.all())
        return format_html(' '.join(res))


class AppRequestTable(tables.Table):
    id = tables.LinkColumn('omaha_request_detail', args=[A('pk')])
    date = tables.DateTimeColumn(accessor='request.created', format='r', order_by='-request__created')
    arch = tables.Column(accessor='request.os.arch')
    platform = tables.Column(accessor='request.os.platform')
    os = tables.Column(accessor='request.os.version', verbose_name='OS')
    sp = tables.Column(accessor='request.os.sp', verbose_name='Service pack')
    events = EventsColumn(empty_values=())
    userid = tables.Column(accessor='request.userid', verbose_name='User ID')
    ip = tables.Column(accessor='request.ip', verbose_name='User IP')

    class Meta:
        model = AppRequest
        attrs = {'class': 'paleblue table table-striped table-bordered table-hover table-condensed',
                 'id': 'apprequest-table'}
        fields = ('id', 'version', 'platform', 'os', 'sp', 'arch', 'date', 'events',)


class VersionsTable(tables.Table):
    version = tables.Column(orderable=False)
    number = tables.Column(orderable=False)

    class Meta:
        attrs = {'class': 'paleblue table table-striped table-bordered table-hover table-condensed',
         'id': 'versions-table'}


class VersionsUsageTable(tables.Table):
    userid = tables.Column(accessor='request.userid', verbose_name='UserID')
    nextversion = tables.Column(verbose_name='Current Version')
    last_update = tables.DateTimeColumn(accessor='request.created', order_by='-request__created',
                                        verbose_name='Last update')
    ip = tables.Column(accessor='request.ip')
    platform = tables.Column(accessor='request.os.platform')

    class Meta:
        model = AppRequest
        orderable = False
        attrs = {'class': 'paleblue table table-striped table-bordered table-hover table-condensed',
                 'id': 'usage-table'}
        fields = ('userid', 'nextversion', 'last_update', 'ip', 'platform')
