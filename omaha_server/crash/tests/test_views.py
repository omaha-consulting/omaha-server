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

from django import test
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse

from crash.models import Crash


class CrashViewTest(test.TestCase):
    @test.override_settings(
        CELERY_ALWAYS_EAGER=False,
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=False,
    )
    def test_view(self):
        meta = dict(
            lang='en',
            version='1.0.0.1',
        )
        mini_dump_file = SimpleUploadedFile("minidump.dat", "content")
        form_data = dict(
            app_id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
            user_id='{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}',
            upload_file_minidump=mini_dump_file,
        )

        form_data.update(meta)

        self.assertEqual(Crash.objects.all().count(), 0)
        response = self.client.post(reverse('crash'), form_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Crash.objects.all().count(), 1)
        obj = Crash.objects.get()
        self.assertEqual(response.content, str(obj.pk))
        self.assertDictEqual(obj.meta, meta)
        self.assertEqual(obj.app_id, form_data['app_id'])
        self.assertEqual(obj.user_id, form_data['user_id'])
        self.assertIsNotNone(obj.upload_file_minidump)
