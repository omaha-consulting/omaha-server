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

from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from lxml.etree import XMLSyntaxError

from omaha.builder import build_response


logger = logging.getLogger(__name__)


class UpdateView(View):
    http_method_names = ['post']

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    def post(self, request):
        try:
            response = build_response(request.body)
        except XMLSyntaxError:
            logger.error('UpdateView', exc_info=True, extra=dict(request=request))
            msg = b"""<?xml version="1.0" encoding="utf-8"?>
<data>
    <message>
        Bad Request
    </message>
</data>"""
            return HttpResponse(msg, status=400, content_type="text/html; charset=utf-8")
        return HttpResponse(response, content_type="text/xml; charset=utf-8")
