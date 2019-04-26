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

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from omaha.tests.utils import temporary_media_root

from sparkle.factories import SparkleVersionFactory
from sparkle.serializers import SparkleVersionSerializer


class SparkleVersionSerializerTest(TestCase):
    maxDiff = None

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_serializer(self):
        version = SparkleVersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', False))
        self.assertDictEqual(SparkleVersionSerializer(version).data, dict(
            id=version.id,
            is_enabled=version.is_enabled,
            is_critical=version.is_critical,
            app=version.app.id,
            channel=version.channel.id,
            version=version.version,
            short_version=version.short_version,
            minimum_system_version=version.minimum_system_version,
            release_notes=version.release_notes,
            file=version.file.url,
            file_size=version.file_size,
            dsa_signature=version.dsa_signature,
            created=version.created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            modified=version.modified.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        ))

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_auto_fill_file_size(self):
        version = SparkleVersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', b' ' * 10))
        data = dict(
            app=version.app.id,
            channel=version.channel.id,
            version='2.1',
            release_notes=version.release_notes,
            file=version.file,
        )

        new_version = SparkleVersionSerializer(data=data)
        self.assertTrue(new_version.is_valid())
        new_version_instance = new_version.save()
        self.assertEqual(new_version_instance.file_size, 10)
