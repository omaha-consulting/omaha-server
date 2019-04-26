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

import os

from django import test
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings
from django.db import DataError

from crash.models import Crash, CrashDescription
from crash.factories import CrashFactory, CrashDescriptionFactory


BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
TAR_FILE = os.path.join(TEST_DATA_DIR, 'foo.tar')
TAR_FILE_ONLY_INSTRUMENTAL_FILE = os.path.join(TEST_DATA_DIR, 'foo_only_instrumental_file.tar')


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
        mini_dump_file = SimpleUploadedFile("minidump.dat", b"content")
        form_data = dict(
            appid='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
            userid='{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}',
            upload_file_minidump=mini_dump_file,
        )

        form_data.update(meta)

        self.assertEqual(Crash.objects.all().count(), 0)
        response = self.client.post(reverse('crash'), form_data, REMOTE_ADDR="8.8.8.8")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Crash.objects.all().count(), 1)
        obj = Crash.objects.get()
        self.assertEqual(response.content.decode(), str(obj.pk))
        self.assertDictEqual(obj.meta, meta)
        self.assertEqual(obj.appid, form_data['appid'])
        self.assertEqual(obj.userid, form_data['userid'])
        self.assertIsNotNone(obj.upload_file_minidump)
        self.assertEqual(obj.ip, '8.8.8.8')

    @test.override_settings(
        CELERY_ALWAYS_EAGER=False,
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=False,
    )
    def test_view_empty_ip(self):
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
            meta = dict(
                lang='en',
                version='1.0.0.1',
            )
            mini_dump_file = SimpleUploadedFile("minidump.dat", b"content")
            form_data = dict(
                appid='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
                userid='{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}',
                upload_file_minidump=mini_dump_file,
            )

            form_data.update(meta)

            self.assertEqual(Crash.objects.all().count(), 0)
            response = self.client.post(reverse('crash'), form_data, REMOTE_ADDR="")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Crash.objects.all().count(), 1)
            obj = Crash.objects.get()
            self.assertEqual(response.content.decode(), str(obj.pk))
            self.assertDictEqual(obj.meta, meta)
            self.assertEqual(obj.appid, form_data['appid'])
            self.assertEqual(obj.userid, form_data['userid'])
            self.assertIsNotNone(obj.upload_file_minidump)
            self.assertEqual(obj.ip, None)

    @test.override_settings(
        CELERY_ALWAYS_EAGER=False,
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=False,
    )
    def test_view_tar_file(self):
        meta = dict(
            lang='en',
            version='1.0.0.1',
        )

        with open(TAR_FILE, 'rb') as f:
            mini_dump_file = SimpleUploadedFile("foo.tar", f.read())

        form_data = dict(
            appid='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
            userid='{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}',
            upload_file_minidump=mini_dump_file,
        )

        form_data.update(meta)

        self.assertEqual(Crash.objects.all().count(), 0)
        response = self.client.post(reverse('crash'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Crash.objects.all().count(), 1)
        obj = Crash.objects.get()
        self.assertEqual(response.content.decode(), str(obj.pk))
        self.assertDictEqual(obj.meta, meta)
        self.assertEqual(obj.appid, form_data['appid'])
        self.assertEqual(obj.userid, form_data['userid'])
        self.assertIsNotNone(obj.upload_file_minidump)
        self.assertIsNotNone(obj.archive)

    @test.override_settings(
        CELERY_ALWAYS_EAGER=False,
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=False,
    )
    def test_view_tar_only_instrumental_file(self):
        meta = dict(
            lang='en',
            version='1.0.0.1',
        )

        with open(TAR_FILE_ONLY_INSTRUMENTAL_FILE, 'rb') as f:
            mini_dump_file = SimpleUploadedFile("foo_only_instrumental_file.tar", f.read())

        form_data = dict(
            appid='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
            userid='{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}',
            upload_file_minidump=mini_dump_file,
        )

        form_data.update(meta)

        self.assertEqual(Crash.objects.all().count(), 0)
        response = self.client.post(reverse('crash'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Crash.objects.all().count(), 1)
        obj = Crash.objects.get()
        self.assertEqual(response.content.decode(), str(obj.pk))
        self.assertDictEqual(obj.meta, meta)
        self.assertEqual(obj.appid, form_data['appid'])
        self.assertEqual(obj.userid, form_data['userid'])
        self.assertFalse(obj.upload_file_minidump.name)
        self.assertIsNotNone(obj.archive)


class CrashDescriptionViewTest(test.TestCase):
    def test_get_bad(self):
        # no crash with such id
        response = self.client.get(
            reverse('crash_description', kwargs=dict(pk=10))
        )
        self.assertEqual(response.status_code, 400)

        # crash with description added
        description = CrashDescriptionFactory()
        response = self.client.get(
            reverse('crash_description', kwargs=dict(pk=description.crash.pk))
        )
        self.assertEqual(response.status_code, 400)

    def test_get_good(self):
        crash = CrashFactory()
        comment = 'Crash comment'
        data = dict(
            comment=comment
        )
        response = self.client.get(
            reverse('crash_description', kwargs=dict(pk=crash.pk)),
            data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].initial['description'], comment)

    def test_post_bad(self):
        summary = 'Test summary'
        description = 'Test Description'
        form_data = dict(
            summary=summary,
            description=description
        )

        # no crash with such id
        response = self.client.post(
            reverse('crash_description', kwargs=dict(pk=10)),
            form_data
        )
        self.assertEqual(response.status_code, 400)

        # crash with description added
        description = CrashDescriptionFactory()
        response = self.client.get(
            reverse('crash_description', kwargs=dict(pk=description.crash.pk)),
            form_data
        )
        self.assertEqual(response.status_code, 400)

    def test_post_good(self):
        crash = CrashFactory()
        summary = 'Test summary'
        description = 'Test Description'
        form_data = dict(
            summary=summary,
            description=description
        )

        self.assertEqual(CrashDescription.objects.all().count(), 0)
        response = self.client.post(
            reverse('crash_description', kwargs=dict(pk=crash.pk)),
            form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('crash/crash_description_submitted.html', response.template_name)
        self.assertEqual(CrashDescription.objects.all().count(), 1)
        obj = CrashDescription.objects.get()
        self.assertEqual(obj.crash, crash)
        self.assertEqual(obj.summary, summary)
        self.assertEqual(obj.description, description)
