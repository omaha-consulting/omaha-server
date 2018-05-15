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

from django.views.generic import ListView
from django.http.response import Http404

from sparkle.models import SparkleVersion
from sparkle.statistics import collect_statistics
from omaha.models import Application

logger = logging.getLogger(__name__)


class SparkleView(ListView):
    http_method_names = ['get']
    queryset = SparkleVersion.objects.filter_by_enabled()
    template_name = 'sparkle/appcast.xml'

    def get(self, request, *args, **kwargs):
        self.appname = self.kwargs.get('app_name')
        self.appid = None
        self.channel = self.kwargs.get('channel')

        try:
            app = Application.objects.get(name=self.kwargs.get('app_name'))
            self.appid = app.id
        except Application.DoesNotExist:
            raise Http404

        collect_statistics(request, self.appid, self.channel)   # It should be a celery task
        return super(SparkleView, self).get(self, request, *args, **kwargs)

    def get_queryset(self):
        qs = super(SparkleView, self).get_queryset()
        qs = qs.filter(channel__name=self.channel,
                  app__name=self.appname).order_by('short_version')
        cur_short_version = self.request.GET.get('appVersionShort')
        if cur_short_version:
            cur_version = '.'.join(cur_short_version.split('.')[-2:])
            upper_version = qs.filter(version__gt=cur_version).filter(is_critical=True).order_by('version').first() or \
                            qs.order_by('-version').first()
            return qs.filter(version__lte=upper_version.version, version__gte=cur_version)
        else:
            return qs

    def get_context_data(self, **kwargs):
        context = super(SparkleView, self).get_context_data(**kwargs)
        context['app_name'] = self.appname
        context['channel'] = self.channel
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super(SparkleView, self).render_to_response(context, **response_kwargs)
        response['Content-Type'] = 'text/xml; charset=utf-8'
        return response
