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


class AppRequestTable(tables.Table):
    id = tables.LinkColumn('omaha_request_detail', args=[A('pk')])
    date = tables.DateTimeColumn(accessor='request.created', format='r', order_by='-request__created')
    arch = tables.Column(accessor='request.os.arch')
    platform = tables.Column(accessor='request.os.platform')
    os = tables.Column(accessor='request.os.version', verbose_name='OS')
    sp = tables.Column(accessor='request.os.sp', verbose_name='Service pack')

    class Meta:
        model = AppRequest
        attrs = {'class': 'paleblue table table-striped table-bordered table-hover table-condensed'}
        fields = ('id', 'version', 'platform', 'os', 'sp', 'arch', 'date',)
