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
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, RedirectView
from django.http import HttpResponse, HttpResponseBadRequest

from encryption.utils import generate_rsa_keys
from encryption.models import GeneratedKey


class RecycleKeyView(RedirectView):

    def get(self, request, *args, **kwargs):
        try:
            GeneratedKey.generate()
        except AssertionError as e:
            return HttpResponse(e.message, status=400)

        # from .tasks import decrypt_crash
        # decrypt_crash(9)
        return super(RecycleKeyView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('admin:encryption_generatedkey_changelist')
