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
from collections import OrderedDict

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView
from django_tables2 import SingleTableView
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.core.cache import cache

from dynamic_preferences.forms import global_preference_form_builder
from dynamic_preferences_registry import global_preferences_manager as gpm

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
from omaha.forms import CrashManualCleanupForm, ManualCleanupForm
from omaha.dynamic_preferences_registry import global_preferences

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
        return get_object_or_404(Application, name=self.kwargs.get('name'))

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
        qs = qs.prefetch_related('events')
        qs = qs.order_by('-request__created')
        self.appid = None

        try:
            app = Application.objects.get(name=self.kwargs.get('name'))
            qs = qs.filter(appid=app.id)
            self.appid = app.id
        except Application.DoesNotExist:
            logger.error('RequestListView DoesNotExist', exc_info=True, extra=dict(request=self.request))

        qs = qs.distinct()
        self.filter = AppRequestFilter(self.request.GET, queryset=qs)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super(RequestListView, self).get_context_data(**kwargs)
        context['filter'] = self.filter
        context['app_name'] = self.kwargs.get('name')
        context['app_id'] = self.appid
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


class PreferenceFormView(StaffMemberRequiredMixin, FormView):
    template_name = 'admin/omaha/set_preferences.html'
    registry = global_preferences

    def get_success_url(self):
        return self.request.path

    def get_form_class(self, *args, **kwargs):
        section = self.kwargs.get('section', None)
        form_class = global_preference_form_builder(section=section)
        return form_class

    def get_context_data(self, *args, **kwargs):
        context = super(PreferenceFormView, self).get_context_data(*args, **kwargs)
        context['sections'] = self.registry.sections()
        context['sections'].sort()
        context['cur_section'] = self.kwargs.get('section')
        form = context['form']
        order_fields = ['Crash__limit_size', 'Crash__limit_storage_days', 'Crash__duplicate_number',
                        'Feedback__limit_size', 'Feedback__limit_storage_days', 'SparkleVersion__limit_size',
                        'Symbols__limit_size', 'Version__limit_size', 'Timezone__timezone']
        form.fields = OrderedDict((k, form.fields[k]) for k in order_fields if k in form.fields.keys())
        return context

    def form_valid(self, form):
        form.update_preferences()
        try:
            self.request.session['django_timezone'] = form.cleaned_data['Timezone__timezone']
        except KeyError:
            pass
        messages.add_message(self.request, messages.INFO, 'Preferences were updated')
        return super(PreferenceFormView, self).form_valid(form)


class MonitoringFormView(StaffMemberRequiredMixin, TemplateView):
    template_name = 'admin/omaha/monitoring.html'
    form_class = ManualCleanupForm
    success_url = reverse_lazy('monitoring')

    def get_context_data(self, **kwargs):
        context = super(MonitoringFormView, self).get_context_data(**kwargs)
        omaha_version_size = float(cache.get('omaha_version_size') or 0)/1073741824
        sparkle_version_size = float(cache.get('sparkle_version_size') or 0)/1073741824
        feedbacks_size = float(cache.get('feedbacks_size') or 0)/1073741824
        crashes_size = float(cache.get('crashes_size') or 0)/1073741824
        symbols_size = float(cache.get('symbols_size') or 0)/1073741824

        data = dict(
            omaha_version=dict(label='Omaha Versions', size=omaha_version_size, limit=gpm['Version__limit_size'], percent=omaha_version_size/gpm['Version__limit_size']*100),
            sparkle_version=dict(label='Sparkle Versions', size=sparkle_version_size, limit=gpm['SparkleVersion__limit_size'], percent=sparkle_version_size/gpm['SparkleVersion__limit_size']*100),
            feedbacks=dict(label='Feedbacks', size=feedbacks_size, limit=gpm['Feedback__limit_size'], percent=feedbacks_size/gpm['Feedback__limit_size']*100),
            crashes=dict(label='Crashes',  size=crashes_size, limit=gpm['Crash__limit_size'], percent=crashes_size/gpm['Crash__limit_size']*100),
            symbols=dict(label='Symbols',  size=symbols_size, limit=gpm['Symbols__limit_size'], percent=symbols_size/gpm['Symbols__limit_size']*100),
        )
        full_size = reduce(lambda res, x: res + x['size'], data.values(), 0)
        context.update(data)
        piechart = None
        if full_size:
            pie_data = [(x['label'], x['size']/full_size * 100) for x in data.values()]
            piechart = make_piechart('used_space', pie_data, unit="%")
        context.update({'used_space': piechart})
        return context


class ManualCleanupFormView(StaffMemberRequiredMixin, FormView):
    template_name = 'admin/omaha/manually_deletion.html'
    form_class = CrashManualCleanupForm

    def get_context_data(self, **kwargs):
        context = super(ManualCleanupFormView, self).get_context_data(**kwargs)
        context['tabs'] = (
            ('crash__Crash', 'Crash'),
            ('feedback__Feedback', 'Feedback'),
            ('omaha__Version', 'Omaha Version'),
            ('sparkle__SparkleVersion', 'Sparkle Version'),
            ('crash__Symbols', 'Symbols')
        )
        context['cur_tab'] = self.kwargs.get('model')
        return context

    def get_success_url(self):
        return reverse('monitoring')

    def get_initial(self):
        return {'type': self.kwargs.get('model')}

    def get_form_class(self):
        cur_tab = self.kwargs.get('model')
        if cur_tab == 'crash__Crash':
            return CrashManualCleanupForm
        if cur_tab in ('feedback__Feedback', 'omaha__Version', 'sparkle__SparkleVersion', 'crash__Symbols'):
            return ManualCleanupForm
        raise Http404

    def form_valid(self, form):
        form.cleanup()
        messages.add_message(self.request, messages.INFO, 'Task was added in queue. Execution can take a long time. Check results on Sentry after a while.')
        return super(ManualCleanupFormView, self).form_valid(form)
