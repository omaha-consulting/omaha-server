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

from django.views.generic import ListView, DetailView, RedirectView
from django.http import Http404

from omaha.models import Application, Version
from sparkle.models import SparkleVersion


class AppListView(ListView):
    model = Application
    template_name = 'downloads/application_list.html'


class VersionListView(DetailView):
    model = Application
    template_name = 'downloads/version_list.html'
    context_object_name = 'app'

    def get_object(self, queryset=None):
        return Application.objects.get(name=self.kwargs.get('name'))

    def get_context_data(self, **kwargs):
        context = super(VersionListView, self).get_context_data(**kwargs)
        app = self.get_object()
        context['omaha_version_list'] = Version.objects.filter_by_enabled(app=app).order_by('-version')
        context['sparkle_version_list'] = SparkleVersion.objects.filter(app=app)
        return context


class OmahaLatestVersionRedirectView(RedirectView):
    permanent = False
    model = Version

    def get_redirect_url(self, *args, **kwargs):
        app = self.kwargs['app']
        channel = self.kwargs['channel']
        platform = self.kwargs['platform']
        try:
            version = self.model.objects.filter(app__name=app,
                                                channel__name=channel,
                                                platform__name=platform).latest('version')
        except self.model.DoesNotExist:
            raise Http404
        return version.file.url


class SparkleLatestVersionRedirectView(RedirectView):
    permanent = False
    model = SparkleVersion

    def get_redirect_url(self, *args, **kwargs):
        app = self.kwargs['app']
        channel = self.kwargs['channel']
        try:
            version = self.model.objects.filter(app__name=app,
                                                channel__name=channel).latest('created')
        except self.model.DoesNotExist:
            raise Http404
        return version.file.url
