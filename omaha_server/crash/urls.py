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

from django.conf.urls import url
from django.views.generic.base import TemplateView
from crash.views import CrashFormView, CrashDescriptionFormView


urlpatterns = [
    url(r'^service/crash_report/$', CrashFormView.as_view(), name='crash'),
    url(r'^service/crash_details/(?P<pk>\d+)$', CrashDescriptionFormView.as_view(), name='crash_description'),
    url(r'^service/crash_details/thanks$',
        TemplateView.as_view(template_name="crash/crash_description_submitted.html"),
        name='crash_description_submitted'),
]
