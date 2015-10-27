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

import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest
from crash.forms import CrashFrom, CrashDescriptionForm
from crash.models import Crash
from omaha_server.utils import get_client_ip


class CrashFormView(FormView):
    http_method_names = ('post',)
    form_class = CrashFrom

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CrashFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        meta = self.request.POST.dict()
        meta.pop("appid", None)
        meta.pop("userid", None)
        obj = form.save(commit=False)
        if meta:
            obj.meta = meta
        obj.ip = get_client_ip(self.request)
        obj.save()
        return HttpResponse(obj.pk, status=200)

    def form_invalid(self, form):
        return HttpResponse(json.dumps(form.errors), status=400, content_type='application/json')


class CrashDescriptionFormView(FormView):
    form_class = CrashDescriptionForm
    template_name = 'crash/crash_description.html'
    success_url = reverse_lazy('crash_description_submitted')

    def dispatch(self, request, *args, **kwargs):
        # verify crash_id refers to valid crash object
        try:
            self.crash = Crash.objects.select_related('crash_description').get(pk=self.kwargs.get('pk'))
        except Crash.DoesNotExist:
            return HttpResponseBadRequest('no such crash')

        # verify there is no crash description for that object yet
        try:
            desc = self.crash.crash_description
            return HttpResponseBadRequest('already reported as \"%s\"' % desc.summary)
        except ObjectDoesNotExist:
            pass

        return super(CrashDescriptionFormView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        data = super(CrashDescriptionFormView, self).get_initial()
        data['description'] = self.request.GET.get('comment')
        return data

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.crash = self.crash
        obj.save()
        return super(CrashDescriptionFormView, self).form_valid(form)
