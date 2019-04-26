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

from django.core.files.uploadedfile import SimpleUploadedFile

import factory


class FeedbackFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'feedback.Feedback'

    description = factory.Sequence(lambda n: 'BlackBox Description #%s' % n)
    email = factory.Sequence(lambda n: 'user%s@example.com' % n)
    page_url = factory.Sequence(lambda n: 'http://url%s.com/' % n)

    screenshot = SimpleUploadedFile('./screenshot.png', b' ' * 123)
    blackbox = SimpleUploadedFile('./blackbox.tar', b' ' * 123)
    system_logs = SimpleUploadedFile('./system_logs.zip', b' ' * 123)
    attached_file = SimpleUploadedFile('./attach.zip', b' ' * 123)
    feedback_data = {
        'web_data': {
            'url': 'http://url.com/'
        },
        'common_data': {
            'description': 'description',
            'user_email': 'user@example.com',
      }
    }


class FeedbackDescriptionFactory(FeedbackFactory):
    description = factory.Sequence(lambda n: 'Description #%s' % n)
