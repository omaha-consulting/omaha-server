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

from omaha.models import Application, Channel, Platform, Version, Action, EVENT_DICT_CHOICES
from omaha.models import version_upload_to
from omaha.factories import ApplicationFactory, ChannelFactory, PlatformFactory, VersionFactory
from omaha.tests.utils import temporary_media_root


class ApplicationModelTest(test.SimpleTestCase):
    def test_factory(self):
        app = ApplicationFactory.create()
        self.assertTrue(Application.objects.get(id=app.id))


class ChannelModelTest(test.TestCase):
    def test_factory(self):
        channel = ChannelFactory.create()
        self.assertTrue(Channel.objects.get(id=channel.id))


class PlatformModelTest(test.TestCase):
    def test_factory(self):
        platform = PlatformFactory.create()
        self.assertTrue(Platform.objects.get(id=platform.id))


class VersionModelTest(test.TestCase):
    @temporary_media_root()
    def test_version_upload_to(self):
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', False))
        self.assertEqual(version_upload_to(version, 'chrome_installer.exe'),
                         'build/{}/{}/{}/{}/chrome_installer.exe'.format(
                             version.app.name,
                             version.channel.name,
                             version.platform.name,
                             version.version,
                             version.file.name,
                         ))


    @temporary_media_root()
    def test_factory(self):
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', False))
        self.assertTrue(Version.objects.get(id=version.id))

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_property(self):
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', ''))
        self.assertEqual(version.file_absolute_url,
                         'http://cache.pack.google.com/edgedl/chrome/install/782.112/chrome_installer.exe')
        self.assertEqual(version.file_package_name, 'chrome_installer.exe')
        self.assertEqual(version.file_url,
                         u'http://cache.pack.google.com/edgedl/chrome/install/782.112/')

    @temporary_media_root()
    @test.override_settings(OMAHA_URL_PREFIX='http://example.com')
    def test_property_default_storage(self):
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', ''))
        _url = 'http://example.com/static/media/build/%s/%s/%s/37.0.2062.124/chrome_installer.exe' \
              % (version.app.name, version.channel.name, version.platform.name)
        self.assertEqual(version.file_absolute_url, _url)
        self.assertEqual(version.file_package_name, 'chrome_installer.exe')
        _url = u'http://example.com/static/media/build/%s/%s/%s/37.0.2062.124/' \
               % (version.app.name, version.channel.name, version.platform.name)
        self.assertEqual(version.file_url, _url)

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    @patch('omaha.models.version_upload_to', lambda o, f: f)
    def test_property_s3_meta_data(self):
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', ''))
        self.assertEqual(version.file_package_name, 'chrome_installer.exe')
        self.assertEqual(version.file_url,
                         'http://cache.pack.google.com/edgedl/chrome/install/782.112/')
        self.assertEqual(version.size, 123)

    @temporary_media_root()
    def test_pre_save_callbac(self):
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', b''))
        self.assertEqual(version.file.size, 0)
        self.assertEqual(version.file_hash, '2jmj7l5rSw0yVb/vlWAYkK/YBwk=')


class ActionModelTest(test.TestCase):
    @temporary_media_root()
    def test_get_attributes(self):
        ver = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', False))
        action = Action(
            version=ver,
            arguments='--do-not-launch-chrome',
            event=EVENT_DICT_CHOICES['install'],
            run='chrome_installer.exe'
        )

        self.assertDictEqual(
            action.get_attributes(),
            dict(
                arguments='--do-not-launch-chrome',
                run='chrome_installer.exe',
            ))

        action = Action(
            version=ver,
            terminateallbrowsers=True,
            event=EVENT_DICT_CHOICES['postinstall'],
            other=dict(
                version='13.0.782.112',
                onsuccess='exitsilentlyonlaunchcmd')
        )

        self.assertDictEqual(
            action.get_attributes(),
            dict(
                terminateallbrowsers='true',
                version='13.0.782.112',
                onsuccess='exitsilentlyonlaunchcmd',
            )
        )
