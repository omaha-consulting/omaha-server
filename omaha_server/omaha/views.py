# coding: utf8

from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from builder import build_response


class UpdateView(View):
    http_method_names = ['post']

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    def post(self, request):
        return HttpResponse(build_response(request.body), content_type="text/xml; charset=utf-8")