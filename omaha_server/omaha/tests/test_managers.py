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

from omaha.models import Version
from omaha.factories import VersionFactory
from utils import temporary_media_root


class VersionManagerTest(TestCase):
    @temporary_media_root()
    def test_filter_by_enabled(self):
        version = VersionFactory.create(
            version='37.0.2062.125',
            file=SimpleUploadedFile('./chrome_installer.exe', False))
        version_disabled = VersionFactory.create(
            app=version.app,
            platform=version.platform,
            channel=version.channel,
            is_enabled=False,
            version='38.0.2062.125',
            file=SimpleUploadedFile('./chrome_installer2.exe', False))

        self.assertEqual(Version.objects.all().count(), 2)
        self.assertEqual(Version.objects.filter_by_enabled().count(), 1)
        self.assertIn(version, Version.objects.filter_by_enabled())
        self.assertNotIn(version_disabled, Version.objects.filter_by_enabled())
