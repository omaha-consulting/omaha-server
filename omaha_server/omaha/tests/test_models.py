# coding: utf8

from django import test
from django.core.files.uploadedfile import SimpleUploadedFile

from omaha.models import Application, Channel, Platform, Version
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
    def test_factory(self):
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', False))
        self.assertTrue(Version.objects.get(id=version.id))

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_property(self):
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', ''))
        self.assertEqual(version.file_absolute_url,
                         'http://cache.pack.google.com/edgedl/chrome/install/782.112/chrome_installer.exe')
        self.assertEqual(version.file_package_name, 'chrome_installer.exe')
        self.assertEqual(version.file_url,
                         'http://cache.pack.google.com/edgedl/chrome/install/782.112/')

    @temporary_media_root()
    def test_pre_save_callbac(self):
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', b''))
        self.assertEqual(version.file.size, 0)
        self.assertEqual(version.file_hash, '2jmj7l5rSw0yVb/vlWAYkK/YBwk=')
