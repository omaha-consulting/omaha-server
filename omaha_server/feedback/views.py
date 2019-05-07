# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2015 Crystalnix Limited

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

from copy import copy
import io

from google.protobuf.descriptor import FieldDescriptor
from protobuf_to_dict import protobuf_to_dict, TYPE_CALLABLE_MAP
from raven import Client
from celery import signature

from django.core.files.uploadedfile import SimpleUploadedFile
from django.views.generic import FormView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings

from feedback.forms import FeedbackForm
from feedback.tasks import send_email_feedback
from feedback.proto_gen.extension_pb2 import ExtensionSubmit
from omaha_server.utils import get_client_ip
from .utils import get_file_extension

dsn = getattr(settings, 'RAVEN_CONFIG', None)
if dsn:
    dsn = dsn['dsn']
raven = Client(
    dsn,
    name=getattr(settings, 'HOST_NAME', None),
    release=getattr(settings, 'APP_VERSION', None)
)


class FeedbackFormView(FormView):
    http_method_names = ('post',)
    form_class = FeedbackForm

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(FeedbackFormView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        submit = ExtensionSubmit()
        submit.ParseFromString(self.request.body)
        type_callable_map = copy(TYPE_CALLABLE_MAP)
        type_callable_map[FieldDescriptor.TYPE_BYTES] = lambda x: '[binary content]'
        pb_dict = protobuf_to_dict(
            submit,
            type_callable_map=type_callable_map,
            use_enum_labels=True
        )

        data = dict(
            description=submit.common_data.description,
            email=submit.common_data.user_email,
            page_url=submit.web_data.url,
            feedback_data=pb_dict,
            ip=get_client_ip(self.request)
        )
        files = dict()
        if submit.screenshot.binary_content:
            files['screenshot'] = SimpleUploadedFile(
                'screenshot.png',
                submit.screenshot.binary_content
            )
        if submit.blackbox.data:
            blackbox_name = self.handle_file_extension(
                io.BytesIO(submit.blackbox.data).read(1024)
            )
            files['blackbox'] = SimpleUploadedFile(
                blackbox_name, submit.blackbox.data
            )
        for attach in submit.product_specific_binary_data:
            key = 'attached_file'
            logs_key = 'system_logs'
            if attach.name == 'system_logs.zip' and logs_key not in files:
                key = logs_key
            files[key] = SimpleUploadedFile(attach.name, attach.data)

        kwargs.update(dict(data=data, files=files))
        return kwargs

    def handle_file_extension(self, file_header):
        file_description = get_file_extension(file_header)
        blackbox_name = 'blackbox'
        if file_description['file_extension']:
            blackbox_name += '.%s' % file_description['file_extension']
        else:
            raven.captureMessage(
                'This is file type not supported, mime type: %s' % file_description['mime_type']
            )
        return blackbox_name

    def form_valid(self, form):
        email_sender = getattr(settings, 'EMAIL_SENDER', None)
        email_recipients = getattr(settings, 'EMAIL_RECIPIENTS', None)
        obj = form.save()
        if email_sender and email_recipients:
            (signature("tasks.send_email_feedback",
                       args=(obj.pk, email_sender, email_recipients))
             .apply_async(queue='private', countdown=1))
        return HttpResponse(obj.pk, status=200)

    def form_invalid(self, form):
        message = 'Invalid feedback form: ' + form.errors.as_json()
        raven.captureMessage(message=message, extra=form.cleaned_data)
        return HttpResponseBadRequest(message)
