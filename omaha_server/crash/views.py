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

from django.views.generic import FormView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from forms import CrashFrom


class CrashFormView(FormView):
    http_method_names = ('post',)
    form_class = CrashFrom

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CrashFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        meta = self.request.POST.dict()
        meta.pop("app_id", None)
        meta.pop("user_id", None)
        obj = form.save(commit=False)
        if meta:
            obj.meta = meta
        obj.save()
        return HttpResponse(obj.pk, status=201)

    def form_invalid(self, form):
        return HttpResponse(json.dumps(form.errors), status=400, content_type='application/json')