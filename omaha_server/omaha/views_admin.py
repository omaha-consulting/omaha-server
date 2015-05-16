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

import logging
import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView
from django.utils import timezone
from django_tables2 import SingleTableView
from django.conf import settings
from django.core.urlresolvers import reverse_lazy

from omaha.statistics import (
    get_users_statistics_months,
    get_users_statistics_weeks,
    get_users_versions,
    get_channel_statistics,
)
from omaha.models import Application, AppRequest
from omaha.filters import AppRequestFilter
from omaha.utils import make_piechart, make_discrete_bar_chart
from omaha.filters import EVENT_RESULT, EVENT_TYPE
from omaha.tables import AppRequestTable
from omaha.forms import TimezoneForm


logger = logging.getLogger(__name__)


STATE_CANCELLED = {
    0: 'unknown',
    1: 'init',
    2: 'waiting to check for update',
    3: 'checking for update',
    4: 'update available',
    5: 'waiting to download',
    6: 'retrying download',
    7: 'downloading',
    8: 'download complete',
    9: 'extracting',
    10: 'applying differential patch',
    11: 'ready to install',
    12: 'waiting to install',
    13: 'installing',
    14: 'install complete',
    15: 'paused',
    16: 'no update',
    17: 'error',
}


class StaffMemberRequiredMixin(object):
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(StaffMemberRequiredMixin, self).dispatch(*args, **kwargs)


class StatisticsView(StaffMemberRequiredMixin, ListView):
    template_name = "admin/omaha/statistics.html"
    model = Application
    context_object_name = "app_list"

    def get_context_data(self, **kwargs):
        context = super(StatisticsView, self).get_context_data(**kwargs)

        context['months'] = make_discrete_bar_chart('months', get_users_statistics_months())
        context['weeks'] = make_discrete_bar_chart('weeks', get_users_statistics_weeks())

        return context


class StatisticsDetailView(StaffMemberRequiredMixin, DetailView):
    model = Application
    template_name = 'admin/omaha/statistics_detail.html'
    context_object_name = 'app'

    def get_object(self, queryset=None):
        return Application.objects.get(name=self.kwargs.get('name'))

    def get_context_data(self, **kwargs):
        context = super(StatisticsDetailView, self).get_context_data(**kwargs)

        app = self.object

        now = timezone.now()
        last_week = now - datetime.timedelta(days=7)

        qs = AppRequest.objects.filter(appid=app.id,
                                       request__created__range=[last_week, now])

        context['install_count'] = qs.filter(events__eventtype=2).count()
        context['update_count'] = qs.filter(events__eventtype=3).count()

        context['months'] = make_discrete_bar_chart('months', get_users_statistics_months(app_id=app.id))
        context['weeks'] = make_discrete_bar_chart('weeks', get_users_statistics_weeks(app_id=app.id))
        context['versions'] = make_piechart('versions', get_users_versions(app.id))
        context['channels'] = make_piechart('channels', get_channel_statistics(app.id))

        return context


class RequestListView(StaffMemberRequiredMixin, SingleTableView):
    model = AppRequest
    context_object_name = 'request_list'
    template_name = 'admin/omaha/request_list.html'
    table_class = AppRequestTable

    def get_queryset(self):
        qs = super(RequestListView, self).get_queryset()
        qs = qs.select_related('request', 'request__os',)
        qs = qs.order_by('-request__created')

        try:
            app = Application.objects.get(name=self.kwargs.get('name'))
            qs = qs.filter(appid=app.id)
        except Application.DoesNotExist:
            logger.error('RequestListView DoesNotExist', exc_info=True, extra=dict(request=self.request))

        qs = qs.distinct()
        self.filter = AppRequestFilter(self.request.GET, queryset=qs)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super(RequestListView, self).get_context_data(**kwargs)
        context['filter'] = self.filter
        context['app_name'] = self.kwargs.get('name')
        return context


class AppRequestDetailView(StaffMemberRequiredMixin, DetailView):
    model = AppRequest
    template_name = 'admin/omaha/request_detail.html'

    def get_queryset(self):
        qs = super(AppRequestDetailView, self).get_queryset()
        qs = qs.select_related('request', 'request__os', 'request__hw')
        qs = qs.prefetch_related('events')
        return qs

    def get_context_data(self, **kwargs):
        name = 'Unknown'
        try:
            app_req = self.get_object()
            app = Application.objects.get(id=app_req.appid)
            name = app.name
        except Application.DoesNotExist:
            logger.error('AppRequestDetailView DoesNotExist', exc_info=True, extra=dict(request=self.request))
        context = super(AppRequestDetailView, self).get_context_data(**kwargs)
        context['app_name'] = name
        context['EVENT_RESULT'] = EVENT_RESULT
        context['EVENT_TYPE'] = EVENT_TYPE
        context['STATE_CANCELLED'] = STATE_CANCELLED
        return context


class TimezoneView(StaffMemberRequiredMixin, FormView):
    template_name = 'admin/set_timezone.html'
    form_class = TimezoneForm
    success_url = reverse_lazy('set_timezone')

    def get_initial(self):
        try:
            cur_timezone = self.request.session['django_timezone']
        except KeyError:
            cur_timezone = settings.TIME_ZONE
        return dict(timezone=cur_timezone)

    def form_valid(self, *args, **kwargs):
        self.request.session['django_timezone'] = args[0].cleaned_data['timezone']
        return super(TimezoneView, self).form_valid(*args, **kwargs)