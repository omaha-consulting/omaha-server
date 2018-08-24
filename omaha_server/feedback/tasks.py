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
import os

from django.core.mail.message import EmailMessage
from django.core.files.storage import default_storage

from omaha_server.celery import app

from feedback.models import Feedback


logger =logging.getLogger(__name__)

email_body_tmpl = """
Description: %s
Page URL: %s
User email: %s
User IP: %s
Feedback JSON data: %s
"""

@app.task(name='tasks.send_email_feedback', ignore_result=True, max_retries=12, bind=True)
def send_email_feedback(self, feedback_pk, sender, recipents):
    try:
        feedback = Feedback.objects.get(pk=feedback_pk)
    except Feedback.DoesNotExist as exc:
        logger.error('Failed processing_crash_dump',
                     exc_info=True,
                     extra=dict(crash_pk=feedback_pk))
        raise self.retry(exc=exc, countdown=2 ** send_email_feedback.request.retries)
    recipients = [x.strip() for x in recipents.split(',')]
    body = email_body_tmpl % (
        feedback.description, feedback.page_url, feedback.email,
        feedback.ip, feedback.feedback_data,
    )
    email = EmailMessage("Feedback # %s" % feedback_pk, body, sender, recipients)

    attachments = [
        feedback.screenshot,
        feedback.blackbox,
        feedback.system_logs,
        feedback.attached_file
    ]
    for attach in attachments:
        if attach:
            email.attach(os.path.basename(attach.name), attach.read())

    email.send()
