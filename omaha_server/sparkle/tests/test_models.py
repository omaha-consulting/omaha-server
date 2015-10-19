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

from mock import patch

# from omaha.models import Application, Channel, Platform, Version, Action, EVENT_DICT_CHOICES
from sparkle.models import version_upload_to
from sparkle.factories import SparkleVersionFactory
from omaha.tests.utils import temporary_media_root

class VersionModelTest(test.TestCase):
    @temporary_media_root()
    def test_version_upload_to(self):
        version = SparkleVersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', False))
        self.assertEqual(version_upload_to(version, 'chrome_installer.exe'),
                         'sparkle/{}/{}/{}/chrome_installer.exe'.format(
                             version.app.name,
                             version.channel.name,
                             version.version,     #TODO: Uncomment after merge with master
                         ))

    @patch('sparkle.models.version_upload_to', lambda o, f: f)
    def test_property(self):
        version = SparkleVersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', ''))
        self.assertEqual(version.size, 123)