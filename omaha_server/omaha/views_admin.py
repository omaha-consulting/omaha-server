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

import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views.generic.list import MultipleObjectMixin
from django.utils import timezone
from raven.contrib.django.raven_compat.models import client

from omaha.statistics import (
    get_users_statistics_months,
    get_users_statistics_weeks,
    get_users_versions,
    get_channel_statistics,
)
from omaha.models import Application, AppRequest
from filters import AppRequestFilter
from omaha.utils import make_piechart, make_discrete_bar_chart


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


class RequestListView(StaffMemberRequiredMixin, ListView, MultipleObjectMixin):
    model = AppRequest
    context_object_name = 'request_list'
    template_name = 'admin/omaha/request_list.html'
    paginate_by = 20

    def get_queryset(self):
        qs = super(RequestListView, self).get_queryset()
        qs = qs.select_related('request', 'request__os',)

        try:
            app = Application.objects.get(name=self.kwargs.get('name'))
            qs = qs.filter(appid=app.id)
        except Application.DoesNotExist:
            client.captureException()

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
            client.captureException()
        context = super(AppRequestDetailView, self).get_context_data(**kwargs)
        context['app_name'] = name
        return context
