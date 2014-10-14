# coding: utf8

from django.views.generic import View, ListView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from builder import build_response
from models import Version


class UpdateView(View):
    http_method_names = ['post']

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    def post(self, request):
        return HttpResponse(build_response(request.body), content_type="text/xml; charset=utf-8")


class SparkleView(ListView):
    http_method_names = ['get']
    queryset = Version.objects.all()
    template_name = 'sparkle/appcast.xml'

    def get_queryset(self):
        qs = super(SparkleView, self).get_queryset()
        return qs.filter(platform__name='mac',
                         channel__name=self.kwargs.get('channel'),
                         app__name=self.kwargs.get('app_name'))

    def get_context_data(self, **kwargs):
        context = super(SparkleView, self).get_context_data(**kwargs)
        context['app_name'] = self.kwargs.get('app_name')
        context['channel'] = self.kwargs.get('channel')
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super(SparkleView, self).render_to_response(context, **response_kwargs)
        response['Content-Type'] = 'text/xml; charset=utf-8'
        return response
